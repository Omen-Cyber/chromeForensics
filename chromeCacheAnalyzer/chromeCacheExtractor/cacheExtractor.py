import traceback
from pathlib import Path
class cacheExtractor:

    def __init__(self, cache_dir, out_dir, output_format):
        self.cache_files = []
        self.cache_dir = cache_dir
        self.out_dir = out_dir
        self.output_format = output_format

    try:
        for root, dirs, files in os.walk(cache_dir):
            for file in files:
                self.cache_files.append(os.path.join(root,file))

    except Exception as e:
        print("ERROR: ", e)
        traceback.print_exc()
        exit(1)

    def parse_cache_entries(self):
        for file in self.cache_files:
            try:
                cache_entry = simple_cache_entry(file)
                if cache_entry.cache_file is not None:
                    cache_entry.parse_header()
                    print(cache_entry)
            except Exception as e:
                print("ERROR: ", e)
                traceback.print_exc()
                exit(1)