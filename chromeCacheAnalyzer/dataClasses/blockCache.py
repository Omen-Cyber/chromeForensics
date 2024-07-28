# net/disk_cache/blockfile/disk_format.h

import dataclasses
import datetime
from typing import Optional
from dataClasses.LruData import LruData
from dataClasses.addr import Addr
from utils.binaryReader import BinaryReader


@dataclasses.dataclass(frozen=True)
class blockFileIndexHeader:
    bf_Index_header_magic: int = 0xC103CAC3
    version: Optional[int] = None
    num_entries: Optional[int] = None
    num_bytes_v2: Optional[int] = None
    last_file: Optional[int] = None
    this_id: Optional[int] = None
    stats_addr: Optional['Addr'] = None
    table_length: Optional[int] = None
    crash: Optional[int] = None
    experiment: Optional[int] = None
    create_time: Optional[datetime.datetime] = None
    num_bytes_v3: Optional[int] = None
    lru: Optional['LruData'] = None

    
    @classmethod
    def from_reader(cls, reader: BinaryReader) -> 'blockFileIndexHeader':
        return cls(
            bf_Index_header_magic = reader.read_uint32(),
            version = reader.read_uint32(),
            num_entries = reader.read_int32(),
            num_bytes_v2 = reader.read_uint32(),
            last_file = reader.read_int32(),
            this_id = reader.read_int32(),
            stats_addr = reader.read_addr(),
            table_length = reader.read_int32() or 0x10000,
            crash = reader.read_int32(),
            experiment = reader.read_int32(),
            create_time = reader.read_datetime(),
            num_bytes_v3 = reader.read_int64(),
            lru = LruData.from_reader(reader)
        )
