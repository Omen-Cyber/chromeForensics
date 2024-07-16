# net/disk_cache/blockfile/disk_format.h

import enum
from utils.binaryReader import BinaryReader
import logging

class blockCacheFile:
    def __init__(self, cache_file):
        self.magic_num = None
        self.cache_file_block = cache_file

    class blockFileHeader:
        bf_header_magic = 0xC104CAC3
        file_version = None  
        this_file = None
        next_file = None
        entry_size = None
        num_entries = None
        max_entries = None
        empty_type_counts = None
        hints = None
        updating = None
        user = None
        allocation_map = None

        block_header_size = 8192
        max_blocks = (block_header_size - 80) * 8

        @classmethod
        def from_reader(cls, reader):
            instance = cls()
            instance.bf_header_magic = reader.read_uint32()
            instance.file_version = reader.read_uint32()
            instance.this_file = reader.read_int16()
            instance.next_file = reader.read_int16()
            instance.entry_size = reader.read_int32()
            instance.num_entries = reader.read_int32()
            instance.max_entries = reader.read_int32()
            instance.empty_type_counts = tuple(reader.read_int32() for _ in range(4))
            instance.hints = tuple(reader.read_int32() for _ in range(4))
            instance.updating = reader.read_int32()
            instance.user = tuple(reader.read_int32() for _ in range(5))
            instance.allocation_map = reader.read_raw(cls.max_blocks // 8)
            return instance

    class blockFileIndexHeader:
        bf_Index_header_magic = 0xC103CAC3
        version = None
        num_entries = None
        num_bytes_v2 = None
        last_file = None
        this_id = None
        stats_addr = None
        table_length = None
        crash = None
        experiment = None
        create_time = None
        num_bytes_v3 = None
        lru = None

        @classmethod
        def from_reader(cls, reader):
            instance = cls()
            instance.bf_Index_header_magic = reader.read_uint32()
            instance.version = reader.read_uint32()
            instance.num_entries = reader.read_int32()
            instance.num_bytes_v2 = reader.read_uint32()
            instance.last_file = reader.read_int32()
            instance.this_id = reader.read_int32()
            instance.stats_addr = reader.read_addr()
            instance.table_length = reader.read_int32() or 0x10000
            instance.crash = reader.read_int32()
            instance.experiment = reader.read_int32()
            instance.create_time = reader.read_datetime()
            instance.num_bytes_v3 = reader.read_int64()
            instance.lru = blockCacheFile.LruData.from_reader(reader)
            return instance

    class entryState(enum.IntEnum):
        NORMAL = 0
        EVICTED = 1
        DOOMED = 2

    class entryFlags(enum.IntFlag):
        PARENT_ENTRY = 1 << 0
        CHILD_ENTRY = 1 << 1

    class entryStore:
        def __init__(self, entry_hash, next_entry, rankings_node, reuse_count, refetch_count, state, creation_time, key_length,
                     long_key_addr, data_sizes, data_addrs, flags, self_hash, key):
            self.entry_hash = entry_hash
            self.next_entry = next_entry
            self.rankings_node = rankings_node
            self.reuse_count = reuse_count
            self.refetch_count = refetch_count
            self.state = state
            self.creation_time = creation_time
            self.key_length = key_length
            self.long_key_addr = long_key_addr
            self.data_sizes = data_sizes
            self.data_addrs = data_addrs
            self.flags = flags
            self.self_hash = self_hash
            self.key = key

        @property
        def key_is_external(self) -> bool:
            return self.long_key_addr.is_initialized

        @classmethod
        def from_bytes(cls, buffer: bytes):
            with BinaryReader.from_bytes(buffer) as reader:
                return cls.from_reader(reader)

        @classmethod
        def from_reader(cls, reader):
            try:
                entry_hash = reader.read_uint32()
                next_entry = reader.read_addr()
                rankings_node = reader.read_addr()
                reuse_count = reader.read_int32()
                refetch_count = reader.read_int32()
                state = blockCacheFile.entryState(BinaryReader.read_int32())
                creation_time = reader.read_datetime()
                key_length = reader.read_int32()
                long_key_addr = reader.read_addr()
                data_sizes = (reader.read_int32(), reader.read_int32(), reader.read_int32(), reader.read_int32())
                data_addrs = (reader.read_addr(), reader.read_addr(), reader.read_addr(), reader.read_addr())
                flags = blockCacheFile.entryFlags(reader.read_uint32())
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

    class LruData:
        def __init__(self, filled, sizes, heads, tails, transactions, operation, operation_list):
            self.filled = filled
            self.sizes = sizes
            self.heads = heads
            self.tails = tails
            self.transactions = transactions
            self.operation = operation
            self.operation_list = operation_list

        @classmethod
        def from_bytes(cls, buffer: bytes):
            with BinaryReader.from_bytes(buffer) as reader:
                return cls.from_reader(reader)

        @classmethod
        def from_reader(cls, reader: BinaryReader):
            filled = reader.read_int32()
            sizes = tuple(reader.read_int32() for _ in range(5))
            heads = tuple(reader.read_addr() for _ in range(5))
            tails = tuple(reader.read_addr() for _ in range(5))
            transactions = reader.read_addr()
            operation = reader.read_int32()
            operation_list = reader.read_int32()
            _ = [reader.read_int32() for _ in range(7)]

            return cls(filled, sizes, heads, tails, transactions, operation, operation_list)