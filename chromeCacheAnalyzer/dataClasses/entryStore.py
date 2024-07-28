# net/disk_cache/blockfile/disk_format.h

import logging
import enum
import datetime
import dataclasses
from typing import Tuple, Optional
from dataClasses.addr import Addr
from utils.binaryReader import BinaryReader


class entryState(enum.IntEnum):
    NORMAL = 0
    EVICTED = 1
    DOOMED = 2


class entryFlags(enum.IntFlag):
    PARENT_ENTRY = 1 << 0
    CHILD_ENTRY = 1 << 1


@dataclasses.dataclass(frozen=True)
class entryStore:
    entry_hash: int
    next_entry: 'Addr'
    rankings_node: 'Addr'
    reuse_count: int
    refetch_count: int
    state: 'entryState'
    creation_time: datetime.datetime
    key_length: int
    long_key_addr: 'Addr'
    data_sizes: Tuple[int, int, int, int]
    data_addrs: Tuple['Addr', 'Addr', 'Addr', 'Addr']
    flags: 'entryFlags'
    self_hash: int
    key: Optional[str]

    @property
    def key_is_external(self) -> bool:
        return self.long_key_addr.is_initialized

    @classmethod
    def from_bytes(cls, buffer: bytes) -> 'entryStore':
        with BinaryReader.from_bytes(buffer) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_reader(cls, reader: BinaryReader) -> 'entryStore':
        try:
            entry_hash = reader.read_uint32()
            next_entry = reader.read_addr()
            rankings_node = reader.read_addr()
            reuse_count = reader.read_int32()
            refetch_count = reader.read_int32()
            state = entryState(reader.read_int32())
            creation_time = reader.read_datetime()
            key_length = reader.read_int32()
            long_key_addr = reader.read_addr()
            data_sizes = tuple(reader.read_int32() for _ in range(4))
            data_addrs = tuple(reader.read_addr() for _ in range(4))
            flags = entryFlags(reader.read_uint32())
            _ = [reader.read_int32() for _ in range(4)]
            self_hash = reader.read_uint32()

            key = None
            if not long_key_addr.is_initialized:
                key = reader.read_utf8(key_length)

            return cls(
                entry_hash, next_entry, rankings_node, reuse_count, refetch_count, state, creation_time, key_length,
                long_key_addr, data_sizes, data_addrs, flags, self_hash, key)
        except Exception as e:
            logging.error(f"Error reading entryStore: {e}")
            raise
