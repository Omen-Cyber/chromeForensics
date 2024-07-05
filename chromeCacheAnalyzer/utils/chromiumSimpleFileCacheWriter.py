class ChromiumSimpleFileCache(ChromiumCache):
    # net/disk_cache/simple/simple_entry_format.h

    _STREAM_0_1_FILENAME_PATTERN = re.compile(r"^[0-9a-f]{16}_0$")

    def __init__(self, cache_dir: Union[os.PathLike, str]):
        self._cache_dir = pathlib.Path(cache_dir)
        self._file_lookup = types.MappingProxyType(self._build_keys())

    @property
    def cache_dir(self) -> pathlib.Path:
        return self._cache_dir

    def _build_keys(self) -> dict[str, list[pathlib.Path]]:
        lookup: dict[str, list[pathlib.Path]] = {}
        for cache_file in self._cache_dir.iterdir():
            if cache_file.is_file() and ChromiumSimpleFileCache._STREAM_0_1_FILENAME_PATTERN.match(cache_file.name):
                with SimpleCacheFile(cache_file) as cf:
                    lookup.setdefault(cf.key, [])
                    lookup[cf.key].append(cache_file)

        return lookup

    def get_location_for_metadata(self, key: str) -> list[CacheFileLocation]:
        result = []
        for file in self._file_lookup[key]:
            file_length = file.stat().st_size
            with SimpleCacheFile(file) as cf:
                offset = file_length + cf.metadata_start_offset_negative
            result.append(CacheFileLocation(file.name, offset))
        return result

    def get_location_for_cachefile(self, key: str) -> list[CacheFileLocation]:
        result = []
        for file in self._file_lookup[key]:
            with SimpleCacheFile(file) as cf:
                offset = cf.data_start_offset
            result.append(CacheFileLocation(file.name, offset))
        return result

    def get_metadata(self, key: str) -> list[CachedMetadata]:
        result = []
        for file in self._file_lookup[key]:
            with SimpleCacheFile(file) as cf:
                result.append(CachedMetadata.from_buffer(cf.get_stream_0()))
        return result

    def get_cachefile(self, key: str) -> list[bytes]:
        result = []
        for file in self._file_lookup[key]:
            with SimpleCacheFile(file) as cf:
                result.append(cf.get_stream_1())
        return result

    def __enter__(self) -> "ChromiumCache":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def close(self):
        pass

    def keys(self) -> Iterable[str]:
        yield from self._file_lookup.keys()

    def get_file_for_key(self, key) -> list[str]:
        return [x.name for x in self._file_lookup[key]]