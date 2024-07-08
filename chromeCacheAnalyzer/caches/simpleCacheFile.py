import logging
from pathlib import Path
from chromeCacheAnalyzer.utils.binaryReader import BinaryReader as br
class simpleCacheFile:
# net/disk_cache/simple/simple_entry_format.h


    def __init__(self,cache_entry, output_dir, output_format):
        self.cache_entry = cache_entry
        self.output_dir = output_dir
        self.output_format = output_format
        self.br = br(self.cache_entry.cache_file_stream)



    def gather_cache_file_headers(self):

        self.cache_entry.magic_num = self.br.read_uint64()
        if self.cache_entry.magic_num != self.cache_entry.simpleCacheHeader.header_intial_magic_number:
            logging.error(f"Invalid magic (expected {self.cache_entry.simpleCacheHeader.header_intial_magic_number}; got {self.cache_entry.magic_num}")
            return False
        self.cache_entry.simpleCacheHeader.header_version = self.br.read_uint32()
        if self.cache_entry.simpleCacheHeader.header_version != 5:
            logging.error(f"Invalid version (expected 5; got {self.cache_entry.simpleCacheHeader.header_version}")
            return False
        self.cache_entry.simpleCacheHeader.header_key_length = self.br.read_uint32()
        if self.cache_entry.simpleCacheHeader.header_key_length == 0:
            logging.error("Invalid key length")
            return False
        self.cache_entry.simpleCacheHeader.header_key_hash = self.br.read_uint32()
        self.br.read_uint32()
        self.cache_entry.simpleCacheHeader.header_key_name = self.br.read_raw(self.cache_entry.simpleCacheHeader.header_key_length).decode("latin-1")
        return True

    def read_cache_file(self):

        simple_cache_entry = self.cache_entry.cache_file_stream


        return True
        '''
        self._reader = BinaryReader(self._path.open("rb"))
        self._header = SimpleCacheHeader.from_reader(self._reader)
        self._key = self._reader.read_raw(self._header.key_length).decode("latin-1")

        # get stream 0 EOF
        self._reader.seek(-SIMPLE_EOF_SIZE, os.SEEK_END)
        try:
            self._stream_0_eof = SimpleCacheEOF.from_reader(self._reader)
        except ValueError as e:
            raise ValueError(f"Error reading EOF for stream 0 in file {self._path}: {e}")
        self._stream_0_start_offset_negative = -SIMPLE_EOF_SIZE - self._stream_0_eof.stream_size
        if self._stream_0_eof.has_key_sha256:
            self._stream_0_start_offset_negative -= 32

        # get stream 1 EOF
        self._reader.seek(-SIMPLE_EOF_SIZE - SIMPLE_EOF_SIZE - self._stream_0_eof.stream_size, os.SEEK_END)
        if self._stream_0_eof.has_key_sha256:
            self._reader.seek(-32, os.SEEK_CUR)
        stream_1_end_offset = self._reader.tell()
        try:
            self._stream_1_eof = SimpleCacheEOF.from_reader(self._reader)
        except ValueError as e:
            raise ValueError(f"Error reading EOF for stream 1 in file {self._path}: {e}")
        self._stream_1_start_offset = SIMPLE_EOF_SIZE + self._header.key_length
        self._stream_1_length = stream_1_end_offset - self._stream_1_start_offset

    def __enter__(self) -> "SimpleCacheFile":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_stream_0(self):
        self._reader.seek(self._stream_0_start_offset_negative, os.SEEK_END)
        return self._reader.read_raw(self._stream_0_eof.stream_size)

    def get_stream_1(self):
        self._reader.seek(self._stream_1_start_offset, os.SEEK_SET)
        return self._reader.read_raw(self._stream_1_length)

    @property
    def data_start_offset(self):
        return self._stream_1_start_offset

    @property
    def metadata_start_offset_negative(self):
        return self._stream_0_start_offset_negative

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def key(self) -> str:
        return self._key

    @property
    def key_hash(self) -> int:
        return self._header.key_hash

    def close(self):
        self._reader.close()
'''

    def write_cache_file(self):
        return True