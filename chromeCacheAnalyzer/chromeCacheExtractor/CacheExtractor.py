import traceback
import logging
import re
from pathlib import Path
from dataClasses.SimpleCacheData import SimpleCacheData as sc
from caches.SimpleCacheFile import SimpleCacheFile as scf
from utils.metaExtractor import extract_data, extract_meta, remove_keys_with_empty_vals



class CacheExtractor:

    def __init__(self, cache_dir, out_dir, output_format):
        self.cache_files = []
        self.cache_dir = Path(cache_dir)
        self.out_dir = Path(out_dir)
        self.output_format = output_format
        self.dynamic_row_headers = set()
        self.rows = []
        logging.basicConfig(level=logging.DEBUG, filename='chrome_cache_analyzer.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    def parse_simple_cache_entries(self):
        try:
            # Iterate over all files in the cache directory
            for cache_file in self.cache_dir.iterdir():
                if cache_file.is_file():
                    logging.info("Parsing SimpleCache file: %s", cache_file)
                    # Open each cache file in binary mode
                    with open(cache_file, 'rb') as c_file:
                        # Create a SimpleCacheFile object with the cache file data
                        cache_entry = scf(sc(c_file.read()), self.out_dir, self.output_format, self.out_dir / "cache_files", self.dynamic_row_headers)

                    # If the cache file stream is not None then add the cache file to the list of cache files
                    if cache_entry.cache_entry.cache_file_stream is not None:
                        self.cache_files.append(cache_entry)

                        # Gather cache file headers
                        if cache_entry.gather_cache_file_headers():

                            # Read binary data from the cache file
                            if cache_entry.read_cache_file():

                                # Getting stream 0 data (HTTP headers and key)
                                stream_0 = cache_entry.get_stream_0()
                                if stream_0:
                                    metadata = cache_entry.parse_headers_from_stream(stream_0)

                                    # row = {"key": cache_entry.cache_entry.SimpleCacheHeader.header_key_name}
                                    row_headers, out_extension, content_encoding = extract_meta(metadata, cache_entry.cache_entry.SimpleCacheHeader.header_key_name, self.dynamic_row_headers)

                                    # Getting stream 1 data (extracted metadata files e.g. javascript, html, css, images)
                                    stream_1 = cache_entry.get_stream_1()
                                    if stream_1:
                                        row = extract_data(stream_1, content_encoding, row_headers, self.out_dir / "cache_files", out_extension)

                                    self.rows.append(row)
                                    print(f"Cache File: {cache_file}\nKey Hash: {cache_entry.cache_entry.SimpleCacheHeader.header_key_hash}\nKey: {cache_entry.cache_entry.SimpleCacheHeader.header_key_name}\n")

            self.rows = remove_keys_with_empty_vals(self.rows)

            # Write the cache file to the output directory
            for cache_entry in self.cache_files:
                cache_entry.rows = self.rows
                cache_entry.dynamic_row_headers = self.dynamic_row_headers
                cache_entry.write_cache_file()
                break
        except Exception as e:
            logging.error(f"Error parsing cache entries: {e}")
            traceback.print_exc()

