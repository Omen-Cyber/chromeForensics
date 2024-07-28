import logging
import os
import traceback
from utils.binaryReader import BinaryReader as br
from dataClasses.simpleCache import simpleCacheFile
from utils.httpResponseParser import responseParser as CachedMetadata
import datetime
import types

EIGHT_BYTE_PICKLE_ALIGNMENT = True  # switch this if you get errors about the EOF magic when doing a Simple Cache
SIMPLE_EOF_SIZE = 24 if EIGHT_BYTE_PICKLE_ALIGNMENT else 20


class simpleCacheFileParser:
    
    
    def __init__(self, cache_entry, output_dir, output_format):
        self.cache_entry = cache_entry
        self.output_dir = output_dir
        self.output_format = output_format
        self.br = br(self.cache_entry.cache_file_stream)

    
    def gather_cache_file_headers(self):
        self.cache_entry.magic_num = self.br.read_uint64()
        if self.cache_entry.magic_num != simpleCacheFile.simpleCacheHeader.header_intial_magic_number:
            logging.error(f"Invalid magic (expected {simpleCacheFile.simpleCacheHeader.header_intial_magic_number}; got {self.cache_entry.magic_num}")
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
        self.br.read_uint32()  # Skipping the padding
        self.cache_entry.simpleCacheHeader.header_key_name = self.br.read_raw(self.cache_entry.simpleCacheHeader.header_key_length).decode("latin-1")
        return True

    
    def gather_cache_eof_data(self):
        eof_data = simpleCacheFile.simpleCacheEOF()
        eof_data.eof_final_magic_number = self.br.read_uint64()
        if eof_data.eof_final_magic_number != simpleCacheFile.simpleCacheEOF.eof_final_magic_number:
            logging.error(f"Invalid magic (expected {simpleCacheFile.simpleCacheEOF.eof_final_magic_number}; got {eof_data.eof_final_magic_number}")
            return None
        eof_data.eof_flags = self.br.read_uint32()
        eof_data.eof_data_crc32 = self.br.read_uint32()
        eof_data.eof_stream_size = self.br.read_uint32()
        return eof_data

    
    def read_cache_file(self):
        try:
            self.br.seek(-SIMPLE_EOF_SIZE, os.SEEK_END)
            self.cache_entry.stream_0_eof = self.gather_cache_eof_data()
            if not self.cache_entry.stream_0_eof:
                raise ValueError("Error reading EOF for stream 0")
            logging.info(f"Stream 0 EOF: {self.cache_entry.stream_0_eof.eof_final_magic_number}, "
                         f"Flags: {self.cache_entry.stream_0_eof.eof_flags}, "
                         f"Stream Size: {self.cache_entry.stream_0_eof.eof_stream_size}")
            self.cache_entry.stream_0_start_offset_negative = -SIMPLE_EOF_SIZE - self.cache_entry.stream_0_eof.eof_stream_size
            if self.cache_entry.stream_0_eof.has_key_sha256():
                self.cache_entry.stream_0_start_offset_negative -= 32
            logging.info(f"Stream 0 start offset negative: {self.cache_entry.stream_0_start_offset_negative}")

            self.br.seek(-SIMPLE_EOF_SIZE - SIMPLE_EOF_SIZE - self.cache_entry.stream_0_eof.eof_stream_size, os.SEEK_END)
            if self.cache_entry.stream_0_eof.has_key_sha256():
                self.br.seek(-32, os.SEEK_CUR)
            stream_1_end_offset = self.br.tell()
            logging.info(f"Stream 1 end offset: {stream_1_end_offset}")
            self.cache_entry.stream_1_eof = self.gather_cache_eof_data()
            if not self.cache_entry.stream_1_eof:
                raise ValueError("Error reading EOF for stream 1")
            logging.info(f"Stream 1 EOF: {self.cache_entry.stream_1_eof.eof_final_magic_number}, "
                         f"Flags: {self.cache_entry.stream_1_eof.eof_flags}, "
                         f"Stream Size: {self.cache_entry.stream_1_eof.eof_stream_size}")
            self.cache_entry.stream_1_start_offset = SIMPLE_EOF_SIZE + self.cache_entry.simpleCacheHeader.header_key_length
            self.cache_entry.stream_1_length = stream_1_end_offset - self.cache_entry.stream_1_start_offset
            logging.info(f"Stream 1 start offset: {self.cache_entry.stream_1_start_offset}, "
                         f"Stream 1 length: {self.cache_entry.stream_1_length}")
            return True
        except Exception as e:
            logging.error(f"Error reading cache file: {e}")
            traceback.print_exc()
            return False

    
    def get_stream_0(self):
        self.br.seek(self.cache_entry.stream_0_start_offset_negative, os.SEEK_END)
        return self.br.read_raw(self.cache_entry.stream_0_eof.eof_stream_size)

    
    def get_stream_1(self):
        self.br.seek(self.cache_entry.stream_1_start_offset, os.SEEK_SET)
        return self.br.read_raw(self.cache_entry.stream_1_length)

    
    def parse_headers_from_stream(self, stream: bytes) -> CachedMetadata:
        metadata = CachedMetadata.from_buffer(stream)
        logging.info("Parsed Headers:")
        for header in metadata.http_header_declarations:
            logging.info(f"Header Declaration: {header}")
        for key, val in metadata.http_header_attributes:
            logging.info(f"Header Attribute: {key}: {val}")
        logging.info(f"Request Time: {metadata.request_time}")
        logging.info(f"Response Time: {metadata.response_time}")
        return metadata

    
    def write_cache_file(self):
        return True

