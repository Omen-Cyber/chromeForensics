#chromium/chromium/blob/main/net/disk_cache/simple/simple_entry_format.h
@dataclasses.dataclass(frozen=True)
class simpleCacheEOF:

    eof_final_magic_number = 0xf4fa6f45970d41d8
    eof_flags: int
    eof_data_crc32: int
    eof_stream_size: int


@dataclasses.dataclass(frozen=True)
class simpleCacheHeader:

    header_intial_magic_number = 0xfcfb6d1ba7725c30
    header_version: int
    header_key_length: int
    header_key_hash: int

@dataclasses.dataclass(frozen=True)
class simpleCacheSparseRangeHeader:

    sparse_magic_number = 0xeb97bf016553676b
    sparse_offset: int
    sparse_length: int
    sparse_data_crc32: int