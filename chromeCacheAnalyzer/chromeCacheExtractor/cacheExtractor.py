import re
import logging
import traceback
from pathlib import Path
from typing import Union 
from caches.simpleCacheFile import simpleCacheFileParser as scfp
from caches.blockCacheFile import blockCacheFileParser as bcfp
from dataClasses.simpleCache import simpleCacheFile as sc
from utils.metaExtractor import extract_meta, extract_data, remove_keys_with_empty_vals



class cacheExtractor:
    def __init__(self, cache_dir: Union[Path, str], out_dir: Union[Path, str], cache_out_dir: Union[Path, str], output_format: str):
        self.cache_dir = Path(cache_dir)
        self.out_dir = Path(out_dir)
        self.cache_out_dir = Path(cache_out_dir)
        self.output_format = output_format
        self.dynamic_row_headers = set()
        self.rows = []
        self.cache_files = []
        logging.basicConfig(level=logging.DEBUG, filename='chrome_cache_analyzer.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    def parse_cache_entries(self):
        logging.info("Gathering cache type")
        data_files = {"data_0", "data_1", "data_2", "data_3"}

        for file in self.cache_dir.iterdir():
            if file.name == "index-dir":
                self.parse_simple_cache_entries()
                return
            elif file.name in data_files:
                self.parse_block_cache_entries()
                return
            elif re.match(r"f_[0-9a-f]{6}", file.name):
                self.parse_block_cache_entries()
                return
            elif re.match(r"^[0-9a-f]{16}_0$", file.name):
                self.parse_simple_cache_entries()
                return

    def parse_simple_cache_entries(self):
        try:
            for cache_file in self.cache_dir.iterdir():
                if cache_file.is_file():
                    logging.info("Parsing SimpleCache file: %s", cache_file)
                    with open(cache_file, 'rb') as c_file:
                        cache_entry = sc(c_file.read())
                        cache_entry_obj = scfp(cache_entry, self.out_dir, self.output_format)

                    if cache_entry_obj.cache_entry.cache_file_stream is not None:
                        self.cache_files.append(cache_entry_obj)
                        logging.info("Gathering cache file headers")
                        if cache_entry_obj.gather_cache_file_headers():
                            logging.info("Gathering cache EOF file")
                            if cache_entry_obj.read_cache_file():
                                logging.info("Getting stream 0")
                                stream_0 = cache_entry_obj.get_stream_0()
                                if stream_0:
                                    logging.info("Parsing headers from stream 0")
                                    metadata = cache_entry_obj.parse_headers_from_stream(stream_0)

                                    row = {"key": cache_entry_obj.cache_entry.simpleCacheHeader.header_key_name}
                                    row, self.dynamic_row_headers, out_extension, content_encoding = extract_meta(metadata, row, self.dynamic_row_headers)

                                    logging.info("Getting stream 1")
                                    stream_1 = cache_entry_obj.get_stream_1()
                                    if stream_1:
                                        logging.info("Extracting data from stream 1")
                                        row = extract_data(stream_1, content_encoding, row, self.cache_out_dir, out_extension)

                                    self.rows.append(row)

                                    logging.info("Writing cache file")
                                    if cache_entry_obj.write_cache_file():
                                        logging.info("Cache file written: %s", self.cache_out_dir / cache_file.name)
                                        print(f"Cache File: {cache_file}\nKey Hash: {cache_entry_obj.cache_entry.simpleCacheHeader.header_key_hash}\nKey: {cache_entry_obj.cache_entry.simpleCacheHeader.header_key_name}\n")

            self.rows = remove_keys_with_empty_vals(self.rows)

        except Exception as e:
            logging.error(f"Error parsing cache entries: {e}")
            traceback.print_exc()

    def parse_block_cache_entries(self):
        try:
            for cache_file in self.cache_dir.rglob('*'):
                if cache_file.is_file():
                    logging.info(f"Parsing BlockCache file: {cache_file}")
                    block_cache_parser = bcfp(cache_file, self.out_dir, self.output_format)

                    if block_cache_parser._index_file.index:
                        logging.info("Parsing Index File")
                        logging.info("Parsing Cache File Header")
                        if block_cache_parser._block_files:
                            logging.info("Parsing Block Entries")
                            block_entries = block_cache_parser._build_keys()
                            if block_entries:
                                logging.info("Parsed Block Entries Successfully")
                                for key, entry in block_entries.items():
                                    row = {"key": key}
                                    row, self.dynamic_row_headers, out_extension, content_encoding = extract_meta(entry, row, self.dynamic_row_headers)

                                    stream_1_data = block_cache_parser.get_data_for_addr(entry.data_addrs[1])
                                    if stream_1_data:
                                        logging.info("Extracting data from stream 1")
                                        row = extract_data(stream_1_data, content_encoding, row, self.out_dir, out_extension)

                                    self.rows.append(row)
                            else:
                                logging.error("Failed to parse block entries")
                        else:
                            logging.error("Failed to parse cache file header")

            self.rows = remove_keys_with_empty_vals(self.rows)

        except Exception as e:
            logging.error(f"Error parsing block cache entries: {e}")
            traceback.print_exc()