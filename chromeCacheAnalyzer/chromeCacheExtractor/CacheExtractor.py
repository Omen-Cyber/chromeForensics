import traceback
import logging
import re
from pathlib import Path
from io import BytesIO


from caches.SimpleCacheFile import SimpleCacheFile as scf
from dataClasses.SimpleCacheData import SimpleCacheData as sc
#from chromeCacheAnalyzer.caches import blockCacheFile


class CacheExtractor:

    def __init__(self, cache_dir, out_dir, output_format):
        # List of cache files data
        self.cache_files = []
        self.cache_dir = Path(cache_dir)
        self.out_dir = Path(out_dir)
        self.output_format = output_format
        self.cache_type = None
        logging.basicConfig(level=logging.DEBUG,filename='chrome_cache_analyzer.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    def parse_cache_entries(self):
        logging.info("Gathering cache type")
        data_files = {"data_0", "data_1", "data_2", "data_3"}

        for file in self.cache_dir.iterdir():
            if file.name == "index-dir":
                self.parse_simple_cache_entries()
                return
            elif file.name in data_files:
                return "ChromiumBlockFileCache"
            elif re.match(r"f_[0-9a-f]{6}", file.name):
                return "ChromiumBlockFileCache"
            elif re.match(r"^[0-9a-f]{16}_0$", file.name):
                self.parse_simple_cache_entries()
                return

    def parse_simple_cache_entries(self):
        try:
            # Iterate over all files in the cache directory
            for cache_file in self.cache_dir.iterdir(): 
                if cache_file.is_file():
                    logging.info("Parsing SimpleCache file: %s", cache_file)
                    # Open each cache file in binary mode
                    with open(cache_file, 'rb') as c_file:
                        # Create a SimpleCacheFile object with the cache file data
                        cache_entry = scf(sc(c_file.read()), self.out_dir, self.output_format)

                    # If the cache file stream is not None then add the cache file to the list of cache files
                    if cache_entry.cache_entry.cache_file_stream is not None:
                        self.cache_files.append(cache_entry)

                        # Gather cache file headers
                        logging.info("Gathering cache file headers")
                        if cache_entry.gather_cache_file_headers():

                            # Read binary data from the cache file
                            logging.info("Reading cache file")
                            if cache_entry.read_cache_file():

                                # Write the cache file to the output directory
                                logging.info("Writing cache file")
                                if cache_entry.write_cache_file():
                                    logging.info("Cache file written: %s", self.cache_out_dir / cache_file.name)
                                    print(f"Cache File: {cache_file}\nKey Hash: {cache_entry.cache_entry.SimpleCacheHeader.header_key_hash}\nKey: {cache_entry.cache_entry.SimpleCacheHeader.header_key_name}\n")

                                

        except Exception as e:
            print("ERROR: ", e)
            exit(1)

    def parse_block_cache_entries(self):
        pass

    def parse_simple_index_entries(self):
        pass

    def parse_block_index_entries(self):
        pass

