#chromium/chromium/blob/main/net/disk_cache/simple/simple_entry_format.h

class simpleCacheFile:

    def __init__(self, cache_file):
        self.magic_num = None
        self.cache_file_stream = cache_file

    class simpleCacheEOF:

        eof_final_magic_number = 0xf4fa6f45970d41d8
        eof_flags = None
        eof_data_crc32 = None
        eof_stream_size = None


    class simpleCacheHeader:

        header_intial_magic_number = 0xfcfb6d1ba7725c30
        header_version = None
        header_key_length = None
        header_key_hash = None
        header_key_name = None



    class simpleCacheSparseRangeHeader:

        sparse_magic_number = 0xeb97bf016553676b
        sparse_offset = None
        sparse_length = None
        sparse_data_crc32 = None