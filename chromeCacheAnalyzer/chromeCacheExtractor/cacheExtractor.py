import traceback
import logging
import re
from pathlib import Path
from io import BytesIO


from chromeCacheAnalyzer.caches.simpleCacheFile import simpleCacheFile as scf
from chromeCacheAnalyzer.dataClasses.simpleCache import simpleCacheFile as sc
#from chromeCacheAnalyzer.caches import blockCacheFile
class cacheExtractor:

    def __init__(self, cache_dir, out_dir, output_format):
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
            elif file.name in data_files:
                return "ChromiumBlockFileCache"
            elif re.match(r"f_[0-9a-f]{6}", file.name):
                return "ChromiumBlockFileCache"
            elif re.match(r"^[0-9a-f]{16}_0$", file.name):
                self.parse_simple_cache_entries()

        return None

    def parse_simple_cache_entries(self):
        try:
            for cache_file in self.cache_dir.iterdir():
                if cache_file.is_file():
                    logging.info("Parsing SimpleCache file: %s", cache_file)
                    with open(cache_file, 'rb') as c_file:
                        cache_entry = scf(sc(c_file.read()), self.out_dir, self.output_format)

                    if cache_entry.cache_entry.cache_file_stream is not None:
                        self.cache_files.append(cache_entry)
                        logging.info("Gathering cache file headers")
                        if cache_entry.gather_cache_file_headers():
                            logging.info("Reading cache file")
                            if cache_entry.read_cache_file():
                                logging.info("Writing cache file")
                                if cache_entry.write_cache_file():
                                    logging.info("Cache file written: %s", self.out_dir / cache_file)
                                    print(cache_file,cache_entry.cache_entry.simpleCacheHeader.header_key_hash,cache_entry.cache_entry.simpleCacheHeader.header_key_name)

        except Exception as e:
            print("ERROR: ", e)
            exit(1)