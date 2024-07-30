import logging
import traceback
from pathlib import Path
from utils.binaryReader import BinaryReader as br
from dataClasses.SimpleCacheData import SimpleCacheData
from utils.httpResponseParser import ResponseParser
from utils.metaExtractor import extract_meta, extract_data, remove_keys_with_empty_vals
import os
import json
import csv
import datetime

EIGHT_BYTE_PICKLE_ALIGNMENT = True  # switch this if you get errors about the EOF magic when doing a Simple Cache
SIMPLE_EOF_SIZE = 24 if EIGHT_BYTE_PICKLE_ALIGNMENT else 20

def json_serial(obj):
    """JSON serializer for objects not serializable by default JSON code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type not serializable")



class SimpleCacheFile:
    # Information from net/disk_cache/simple/simple_entry_format.h

    def __init__(self, cache_entry, output_dir, output_format, cache_out_dir, dynamic_row_headers):
        self.cache_entry = cache_entry
        self.output_dir = Path(output_dir)
        self.output_format = output_format
        self.cache_out_dir = Path(cache_out_dir)
        self.cache_out_dir.mkdir(parents=True, exist_ok=True)
        self.br = br(self.cache_entry.cache_file_stream)
        self.log_entries = []
        self.rows = []
        self.dynamic_row_headers = dynamic_row_headers

    # Gather the cache file headers
    def gather_cache_file_headers(self):
        self.cache_entry.magic_num = self.br.read_uint64()
        if self.cache_entry.magic_num != self.cache_entry.SimpleCacheHeader.header_intial_magic_number:
            msg = f"Invalid magic (expected {self.cache_entry.SimpleCacheHeader.header_intial_magic_number}; got {self.cache_entry.magic_num}"
            logging.error(msg)
            return False
        self.cache_entry.SimpleCacheHeader.header_version = self.br.read_uint32()
        if self.cache_entry.SimpleCacheHeader.header_version != 5:
            msg = f"Invalid version (expected 5; got {self.cache_entry.SimpleCacheHeader.header_version}"
            logging.error(msg)
            return False
        self.cache_entry.SimpleCacheHeader.header_key_length = self.br.read_uint32()
        if self.cache_entry.SimpleCacheHeader.header_key_length == 0:
            msg = "Invalid key length"
            logging.error(msg)
            return False
        self.cache_entry.SimpleCacheHeader.header_key_hash = self.br.read_uint32()
        self.br.read_uint32()
        self.cache_entry.SimpleCacheHeader.header_key_name = self.br.read_raw(self.cache_entry.SimpleCacheHeader.header_key_length).decode("latin-1")
        return True

    def check_for_simple_eof(self):
        eof_data = SimpleCacheData.SimpleCacheEOF()
        eof_data.eof_final_magic_number = self.br.read_uint64()
        if eof_data.eof_final_magic_number != SimpleCacheData.SimpleCacheEOF.eof_final_magic_number:
            msg = f"Invalid magic number: {eof_data.eof_final_magic_number}; Expected: {SimpleCacheData.SimpleCacheEOF.eof_final_magic_number}"
            logging.error(msg)
            return None
        eof_data.eof_flags = self.br.read_uint32()
        eof_data.eof_data_crc32 = self.br.read_uint32()
        eof_data.eof_stream_size = self.br.read_uint32()
        return eof_data

    def read_cache_file(self):

        # Read the last 24 bytes of the file to get the EOF for stream 0                        #
        # Calculate the start offset and length for stream 0 from the EOF position              #
        # Adjust the offset if there is an additional SHA256 key                                #
        # Move the file pointer to the position of the EOF marker for stream1                   #
        # Adjust the position for the SHA265 key if it exists                                   #
        # Get the current position as the end offset of steam1                                  #
        # Read the EOF data for stream1                                                         #
        # If the EOF data for steam1 is not read correctly, raise an error and log the data     #
        # Calculate the start offset and length for stream 1 from the EOF position              #
        # Log any errors that occur and print the stack trace                                   #
        # Retrieve data for stream 0 from the cache file                                        #
        # Retrieve data for stream 1 from the cache file                                        #
        # Parse the headers from the raw stream data using the 'ResponseParser' Class           #
        # Write the cache file


        try:
            # Seek to the end of the file and read the EOF for stream 0
            self.br.seek(-SIMPLE_EOF_SIZE, os.SEEK_END)
            self.cache_entry.stream_0_eof = self.check_for_simple_eof()

            # Check if the EOF for stream0 was read correctly
            if not self.cache_entry.stream_0_eof:
                raise ValueError("Error reading EOF for stream 0")
            msg = (f"Stream 0 EOF: {self.cache_entry.stream_0_eof.eof_final_magic_number}, "
                   f"Flags: {self.cache_entry.stream_0_eof.eof_flags},"
                   f"Stream Size: {self.cache_entry.stream_0_eof.eof_stream_size}")
            logging.info(msg)

            # Calculate the start offset for stream 0
            self.cache_entry.stream_0_start_offset_negative = -SIMPLE_EOF_SIZE - self.cache_entry.stream_0_eof.eof_stream_size
            
            # Check if stream0 has a sha256 key and adjust the start offset accordingly
            if self.cache_entry.stream_0_eof.has_sha256_key():
                self.cache_entry.stream_0_start_offset_negative -= 32
            msg = f"Stream 0 start offset negative: {self.cache_entry.stream_0_start_offset_negative}"
            logging.info(msg)

            # Move the file pointer to the position of the EOF marker for stream1
            self.br.seek(-SIMPLE_EOF_SIZE - SIMPLE_EOF_SIZE - self.cache_entry.stream_0_eof.eof_stream_size, os.SEEK_END)
            
            # Adjust the position for the SHA265 key if it existss
            if self.cache_entry.stream_0_eof.has_sha256_key():
                self.br.seek(-32, os.SEEK_CUR)

            # Get the current position as the end offset of steam1    
            stream_1_end_offset = self.br.tell()
            msg = f"Stream 1 end offset: {stream_1_end_offset}"
            logging.info(msg)
            
            # Read the EOF data for stream1
            self.cache_entry.stream_1_eof = self.check_for_simple_eof()

            # If the EOF data for steam1 is not read correctly, raise an error and log the data
            if not self.cache_entry.stream_1_eof:
                raise ValueError("Error reading EOF for stream 1")
            msg = (f"Stream 1 EOF: {self.cache_entry.stream_1_eof.eof_final_magic_number}, "
                   f"Flags: {self.cache_entry.stream_1_eof.eof_flags}, "
                   f"Stream Size: {self.cache_entry.stream_1_eof.eof_stream_size}")
            logging.info(msg)

            # Calculate the start offset and length for stream 1 from the EOF position
            self.cache_entry.stream_1_start_offset = SIMPLE_EOF_SIZE + self.cache_entry.SimpleCacheHeader.header_key_length
            self.cache_entry.stream_1_length = stream_1_end_offset - self.cache_entry.stream_1_start_offset
            msg = (f"Stream 1 start offset: {self.cache_entry.stream_1_start_offset}, "
                   f"Stream 1 length: {self.cache_entry.stream_1_length}")
            logging.info(msg)

            return True
        except Exception as e:
            msg = f"Error reading cache file: {e}"
            logging.error(msg)
            traceback.print_exc()
            return False

    # Retrieve data for stream 0 from the cache file
    def get_stream_0(self):
        self.br.seek(self.cache_entry.stream_0_start_offset_negative, os.SEEK_END)
        return self.br.read_raw(self.cache_entry.stream_0_eof.eof_stream_size)

    # Retrieve data for stream 1 from the cache file
    def get_stream_1(self):
        self.br.seek(self.cache_entry.stream_1_start_offset, os.SEEK_SET)
        return self.br.read_raw(self.cache_entry.stream_1_length)

    # Parse the headers from the raw stream data using the 'ResponseParser' Class
    def parse_headers_from_stream(self, stream: bytes) -> ResponseParser:
        metadata = ResponseParser.from_buffer(stream)
        msg = "Parsed Headers:"
        logging.info(msg)
        for header in metadata.http_header_declarations:
            msg = f"Header Declaration: {header}"
            logging.info(msg)
        for key, val in metadata.http_header_attributes:
            msg = f"Header Attribute: {key}: {val}"
            logging.info(msg)
        msg = f"Request Time: {metadata.request_time}"
        logging.info(msg)
        msg = f"Response Time: {metadata.response_time}"
        logging.info(msg)
        return metadata

    # Write the cache file
    def write_cache_file(self):
        try:
            default_row_headers = ["file_hash", "metadata_link", "key", "request_time", "response_time", "date"]

            # Write to the appropriate format
            if self.output_format == 'csv':
                csv_out_f = (self.output_dir / "cache_report.csv").open("wt", encoding="utf-8", newline="")
                csv_out_f.write("\ufeff")
                csv_out = csv.DictWriter(
                    csv_out_f, fieldnames=default_row_headers + sorted(self.dynamic_row_headers), dialect=csv.excel,
                    quoting=csv.QUOTE_ALL, quotechar="\"", escapechar="\\")
                csv_out.writeheader()
                for row in self.rows:
                    csv_out.writerow(row)
                csv_out_f.close()
            elif self.output_format == 'json':
                json_out_p = self.output_dir / "cache_report.json"
                with json_out_p.open("w", encoding="utf-8", errors='replace') as json_out_f:
                    json.dump(self.rows, json_out_f, ensure_ascii=False, indent=4, default=json_serial)


            return True
        except Exception as e:
            msg = f"Error writing cache file: {e}"
            logging.error(msg)
            traceback.print_exc()
            return False
