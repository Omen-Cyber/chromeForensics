#chromium/chromium/blob/main/net/disk_cache/simple/simple_entry_format.h


class SimpleCacheData:

    def __init__(self, cache_file):
        self.magic_num = None
        self.cache_file_stream = cache_file

    class SimpleCacheEOF:

        eof_final_magic_number = 0xf4fa6f45970d41d8
        eof_flags = None
        #eof_data_crc32 = None
        eof_stream_size = None

        def has_crc(self):
            return self.eof_flags & 1 > 0

        def has_sha256_key(self):
            return self.eof_flags & 2 > 0


    class SimpleCacheHeader:

        header_intial_magic_number = 0xfcfb6d1ba7725c30
        header_version = None
        header_key_length = None
        header_key_hash = None
        header_key_name = None



    class SimpleCacheSparseRangeHeader:

        sparse_magic_number = 0xeb97bf016553676b
        sparse_offset = None
        sparse_length = None
        sparse_data_crc32 = None