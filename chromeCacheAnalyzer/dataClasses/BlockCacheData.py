@dataclasses.dataclass(frozen=True)
class BlockFileIndexHeader:
    # net/disk_cache/blockfile/disk_format.h
    version: int
    num_entries: int
    num_bytes_v2: int
    last_file: int
    this_id: int
    stats_addr: Addr
    table_length: int
    crash: int
    experiment: int
    create_time: datetime.datetime
    num_bytes_v3: int
    lru: LruData
    blockMagicNumber = 0xC103CAC3

@dataclasses.dataclass(frozen=True)
class EntryState(enum.IntEnum):
    NORMAL = 0
    EVICTED = 1
    DOOMED = 2

@dataclasses.dataclass(frozen=True)
class EntryFlags(enum.IntFlag):
    PARENT_ENTRY = 1 << 0
    CHILD_ENTRY = 1 << 1

@dataclasses.dataclass(frozen=True)
class EntryStore:
    entry_hash: int
    next_entry: Addr
    rankings_node: Addr
    reuse_count: int
    refetch_count: int
    state: EntryState
    creation_time: datetime
    key_length: int
    long_key_addr: Addr
    data_sizes: tuple[int, int, int, int]
    data_addrs: tuple[Addr, Addr, Addr, Addr]
    flags: EntryFlags
    self_hash: int
    key: Optional[str]

@dataclasses.dataclass(frozen=True)
class LruData:
    filled: int
    sizes: typing.Collection[int]
    heads: typing.Collection[Addr]
    tails: typing.Collection[Addr]
    transactions: Addr
    operation: int
    operation_list: int

@dataclasses.dataclass(frozen=True)
class FileType(enum.IntEnum):
# net/disk_cache/blockfile/disk_format.h

    EXTERNAL = 0
    RANKINGS = 1
    BLOCK_256 = 2
    BLOCK_1K = 3
    BLOCK_4K = 4
    BLOCK_FILES = 5
    BLOCK_ENTRIES = 6
    BLOCK_EVICTED = 7


_BLOCKSIZE_FOR_FILETYPE = {
    FileType.RANKINGS: 36,
    FileType.BLOCK_256: 256,
    FileType.BLOCK_1K: 1024,
    FileType.BLOCK_4K: 4096,
    FileType.BLOCK_FILES: 8,
    FileType.BLOCK_ENTRIES: 104,
    FileType.BLOCK_EVICTED: 48,
    FileType.EXTERNAL: 0
}


_BLOCK_FILE_FILETYPE = {FileType.BLOCK_256, FileType.BLOCK_1K, FileType.BLOCK_4K}