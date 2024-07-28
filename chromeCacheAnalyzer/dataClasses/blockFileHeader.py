 # net/disk_cache/blockfile/disk_format_base.h

import dataclasses
from typing import Optional, Tuple
from utils.binaryReader import BinaryReader

@dataclasses.dataclass(frozen=True)
class blockFileHeader:
    bf_header_magic: int = 0xC104CAC3
    file_version: Optional[int] = None
    this_file: Optional[int] = None
    next_file: Optional[int] = None
    entry_size: Optional[int] = None
    num_entries: Optional[int] = None
    max_entries: Optional[int] = None
    empty_type_counts: Optional[Tuple[int, int, int, int]] = None
    hints: Optional[Tuple[int, int, int, int]] = None
    updating: Optional[int] = None
    user: Optional[Tuple[int, int, int, int, int]] = None
    allocation_map: Optional[bytes] = None

    block_header_size: int = 8192
    max_blocks: int = (block_header_size - 80) * 8

    @classmethod
    def from_reader(cls, reader: BinaryReader) -> 'blockFileHeader':
        return cls(
            bf_header_magic = reader.read_uint32(),
            file_version = reader.read_uint32(),
            this_file = reader.read_int16(),
            next_file = reader.read_int16(),
            entry_size = reader.read_int32(),
            num_entries = reader.read_int32(),
            max_entries = reader.read_int32(),
            empty_type_counts = tuple(reader.read_int32() for _ in range(4)),
            hints = tuple(reader.read_int32() for _ in range(4)),
            updating = reader.read_int32(),
            user = tuple(reader.read_int32() for _ in range(5)),
            allocation_map = reader.read_raw(cls.max_blocks // 8)
        )
