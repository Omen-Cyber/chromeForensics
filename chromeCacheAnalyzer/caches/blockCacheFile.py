import logging
from pathlib import Path
from typing import Union, Dict, Tuple, BinaryIO, Optional
from utils.binaryReader import BinaryReader as br
from utils.addrParser import Addr, FileType, _BLOCK_FILE_FILETYPE
from dataClasses.blockCache import blockCacheFile as bc
from utils.metadataParser import CachedMetadata

class blockCacheFileParser:
    def __init__(self, cache_file: Union[Path, str], output_dir: Union[Path, str], output_format: str):
        self._in_dir = Path(cache_file).parent
        self._index_file_path = self._find_index_file(self._in_dir)
        if not self._index_file_path:
            raise FileNotFoundError(f"Index file not found in cache directory: {self._in_dir}")
        self._block_files: Dict[int, Tuple[bc.blockFileHeader, BinaryIO]] = {}
        self._keys = self._build_keys()
        self.output_dir = Path(output_dir)
        self.output_format = output_format
        self.index = []
        self.block_entries = []

    def _find_index_file(self, directory: Path) -> Optional[Path]:
        for path in directory.rglob('*'):
            if path.name == "index":
                return path
        return None

    def _get_block_file(self, block_file_number: int) -> Tuple[bc.blockFileHeader, BinaryIO]:
        if cached := self._block_files.get(block_file_number):
            return cached

        block_file_stream = (self._in_dir / f"data_{block_file_number}").open("rb")
        header = bc.blockFileHeader.from_reader(br(block_file_stream.read(bc.blockFileHeader.block_header_size)))
        self._block_files[block_file_number] = (header, block_file_stream)
        return header, block_file_stream

    def _build_keys(self) -> Dict[str, bc.entryStore]:
        result = {}
        with open(self._index_file_path, "rb") as index_file:
            reader = br(index_file.read())
            index_header = bc.blockFileIndexHeader.from_reader(reader)
            for addr in index_header.index:
                while addr.is_initialized:
                    raw = self.get_data_for_addr(addr)
                    es = bc.entryStore.from_bytes(raw)
                    key = es.key if es.key else self.get_data_for_addr(es.long_key_addr).decode("utf-8")
                    result[key] = es
                    addr = es.next_entry
        return result

    def get_data_for_addr(self, addr: Addr) -> bytes:
        if not addr.is_initialized:
            raise ValueError("Addr is not initialized")
        if addr.file_type == FileType.EXTERNAL:
            with (self._in_dir / f"f_{addr.external_file_number:06x}").open("rb") as f:
                return f.read()
        elif addr.file_type in _BLOCK_FILE_FILETYPE:
            block_header, stream = self._get_block_file(addr.file_selector)
            stream.seek(bc.blockFileHeader.block_header_size + (block_header.entry_size * addr.block_number))
            return stream.read(block_header.entry_size * addr.contiguous_blocks)
        raise ValueError(f"Unexpected file type: {addr.file_type}")

    def get_data_buffer(self, key: Union[str, bc.entryStore], stream_number: int) -> Optional[bytes]:
        if stream_number < 0 or stream_number > 2:
            raise ValueError("invalid stream number")
        es = self._keys[key] if isinstance(key, str) else key
        addr = es.data_addrs[stream_number]
        if not addr.is_initialized:
            return None
        data = self.get_data_for_addr(addr)
        if len(data) < es.data_sizes[stream_number]:
            raise ValueError(f"Could not get all of the data for stream {stream_number}")
        return data[:es.data_sizes[stream_number]]

    def get_metadata(self, key: Union[str, bc.entryStore]) -> list:
        buffer = self.get_data_buffer(key, 0)
        if not buffer:
            return []
        meta = CachedMetadata.from_buffer(buffer)
        return [meta]

    def get_cachefile(self, key: Union[str, bc.entryStore]) -> list[bytes]:
        return [self.get_data_buffer(key, 1)]

    def close(self):
        for _, stream in self._block_files.values():
            stream.close()