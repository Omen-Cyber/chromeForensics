class ChromiumBlockFileCache(ChromiumCache):
# net/disk_cache/blockfile/disk_format.h
    def __init__(self, cache_dir: Union[os.PathLike, str]):
        self._in_dir = pathlib.Path(cache_dir)
        self._index_file = BlockFileIndexFile(self._in_dir / "index")
        self._block_files: dict[int, tuple[BlockFileHeader, BinaryIO]] = {}
        self._keys = self._build_keys()

    def _get_block_file(self, block_file_number: int) -> tuple[BlockFileHeader, BinaryIO]:
        if cached := self._block_files.get(block_file_number):
            return cached

        block_file_stream = (self._in_dir / f"data_{block_file_number}").open("rb")
        header = BlockFileHeader.from_bytes(block_file_stream.read(BlockFileHeader._BLOCK_HEADER_SIZE))
        self._block_files[block_file_number] = (header, block_file_stream)
        return header, block_file_stream

    def _build_keys(self):
        result = {}
        for addr in self._index_file.index:
            while addr.is_initialized:
                raw = self.get_data_for_addr(addr)
                es = EntryStore.from_bytes(raw)
                if es.key is not None:
                    key = es.key
                else:
                    key = self.get_data_for_addr(es.long_key_addr).decode("utf-8")

                result[key] = es
                addr = es.next_entry

        return result

    def _get_location(self, key: str, stream_number: int):
        es = self._keys[key]
        addr = es.data_addrs[stream_number]
        if addr.file_type in _BLOCK_FILE_FILETYPE:
            file_name = f"data_{addr.file_selector}"
            block_header, stream = self._get_block_file(addr.file_selector)
            offset = BlockFileHeader._BLOCK_HEADER_SIZE + (block_header.entry_size * addr.block_number)
            return CacheFileLocation(file_name, offset)
        elif addr.file_type == FileType.EXTERNAL:
            file_name = f"f_{addr.external_file_number:06x}"
            return CacheFileLocation(file_name, 0)

        raise ValueError("unexpected file type")

    def get_location_for_metadata(self, key: str) -> list[CacheFileLocation]:
        return self._get_location(key, 0)

    def get_location_for_cachefile(self, key: str) -> list[CacheFileLocation]:
        return self._get_location(key, 1)

    def get_stream_for_addr(self, addr: Addr) -> BinaryIO:
        if not addr.is_initialized:
            raise ValueError("Addr is not initialized")
        if addr.file_type in _BLOCK_FILE_FILETYPE:
            block_header, stream = self._get_block_file(addr.file_selector)
            stream.seek(BlockFileHeader._BLOCK_HEADER_SIZE + (block_header.entry_size * addr.block_number))
            return io.BytesIO(stream.read(block_header.entry_size * addr.contiguous_blocks))
        elif addr.file_type == FileType.EXTERNAL:
            return (self._in_dir / f"f_{addr.external_file_number:06x}").open("rb")

        raise ValueError("unexpected file type")

    def get_data_for_addr(self, addr: Addr) -> bytes:
        if not addr.is_initialized:
            raise ValueError("Addr is not initialized")
        if addr.file_type in _BLOCK_FILE_FILETYPE:
            block_header, stream = self._get_block_file(addr.file_selector)
            stream.seek(BlockFileHeader._BLOCK_HEADER_SIZE + (block_header.entry_size * addr.block_number))
            return stream.read(block_header.entry_size * addr.contiguous_blocks)
        elif addr.file_type == FileType.EXTERNAL:
            with (self._in_dir / f"f_{addr.external_file_number:06x}").open("rb") as f:
                return f.read()

        raise ValueError("unexpected file type")

    def get_data_buffer(self, key: Union[str, EntryStore], stream_number: int) -> Optional[bytes]:
        if stream_number < 0 or stream_number > 2:
            raise ValueError("invalid stream number")
        if isinstance(key, EntryStore):
            es = key
        else:
            es = self._keys[key]

        addr = es.data_addrs[stream_number]
        if not addr.is_initialized:
            return None

        data = self.get_data_for_addr(addr)
        stream_length = es.data_sizes[stream_number]
        if len(data) < stream_length:
            print(es, file=sys.stderr)
            raise ValueError(f"Could not get all of the data for stream {stream_number}")
        data = data[0:stream_length]
        return data

    def get_metadata(self, key: Union[str, EntryStore]) -> list[CachedMetadata]:
        buffer = self.get_data_buffer(key, 0)
        if not buffer:
            return []
        meta = CachedMetadata.from_buffer(buffer)
        return [meta]

    def get_cachefile(self, key: Union[str, EntryStore]) -> list[bytes]:
        return [self.get_data_buffer(key, 1)]

    def __enter__(self) -> "ChromiumBlockFileCache":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def keys(self) -> Iterable[str]:
        yield from self._keys.keys()

    def values(self) -> Iterable[EntryStore]:
        yield from self._keys.values()

    def items(self) -> Iterable[tuple[str, EntryStore]]:
        yield from self._keys.items()

    def __contains__(self, item) -> bool:
        return item in self._keys

    def __getitem__(self, item) -> EntryStore:
        return self._keys[item]

    def close(self):
        for _, stream in self._block_files.values():
            stream.close()
