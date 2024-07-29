import struct
from argparse import ArgumentParser
import os
import traceback

# The magic number for the index file of blockfile cache
BLOCK_INDEX_MAGIC_NUM = 0xC3CA03C1
# The magic number for the index file simple cache
SIMPLE_INDEX_MAGIC_NUM = 0x656e74657220796f
# The magic numbers for a simple file cache entry
SIMPLE_INITIAL_MAGIC_NUM = 0xfcfb6d1ba7725c30
SIMPLE_FINAL_MAGIC_NUM = 0xf4fa6f45970d41d8
SIMPLE_SPARSE_RANGE_MAGIC_NUM = 0xeb97bf016553676b


def parse_arguments():
    parser = ArgumentParser(description="A tool to extract information from chrome cache files")
    parser.add_argument("-i", "--index", help="Path to the index file")
    parser.add_argument("-d", "--directory", help="Path to the cache directory")
    parser.add_argument("-o", "--output", help="Path to the output directory")
    return parser.parse_args()


# Cache index file parsing for simple cache

class simple_cache_index:

    def __init__(self, index_file):
        try:
            self.header = open(index_file, 'rb')
        except FileNotFoundError:
            print("The file does not exist")
            exit(1)
        self.version = None
        self.entries = None
        self.data_size = None

    def parse_header(self):
        self.header.seek(8)
        self.magic_num = struct.unpack('q', self.header.read(8))[0]

        print(hex(self.magic_num), ":", str(self.SIMPLE_INDEX_MAGIC_NUM))
        if self.magic_num == self.SiMPLE_INDEX_MAGIC_NUM:
            self.version = struct.unpack('I', self.header.read(4))[0]
            self.entries = struct.unpack('q', self.header.read(8))[0]
            self.data_size = struct.unpack('I', self.header.read(4))[0]
            s

    def __str__(self):
        return (f"\
                Minor: {self.minor}\n\
                Major: {self.major}\n\
                Entries: {self.entries}\n\
                Data Size: {self.data_size}\n\
                Last File: {self.last_file}\n\
                Dirty: {self.dirty}\n\
                Table Size: {self.table_size}\n\
                Crash: {self.crash}\n\
                Creation Date: {self.creation}\n")
'''


class simple_cache_entries:

    def __init__(self, cache_dir):
        self.cache_files = []
        self.cache_dir = cache_dir
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


class simple_cache_entry:

    def __init__(self, simple_cache_file):
        self.magic_num = None
        self.version = None
        self.entry_size = None
        self.cache_file = None

        try:
            # Skip the index file
            if simple_cache_file[-5:] != "index":
                print(simple_cache_file)
                self.cache_file = open(simple_cache_file, 'rb')
            else:
                return
        except FileNotFoundError:
            print("The file does not exist")
            traceback.print_exc()
            exit(1)



    def parse_header(self):
        self.magic_num = struct.unpack('Q', self.cache_file.read(8))[0]

        #print(hex(self.magic_num), ":", str(hex(SIMPLE_INITIAL_MAGIC_NUM)))
        if self.magic_num == SIMPLE_INITIAL_MAGIC_NUM:
            self.version = struct.unpack('I', self.cache_file.read(4))[0]
            self.entry_size = struct.unpack('I', self.cache_file.read(4))[0]
'''
    def __str__(self):
        return (f"\
                Minor: {self.minor}\n\
                Major: {self.major}\n\
                Entries: {self.entries}\n\
                Data Size: {self.data_size}\n\
                Last File: {self.last_file}\n\
                Dirty: {self.dirty}\n\
                Table Size: {self.table_size}\n\
                Crash: {self.crash}\n\
                Creation Date: {self.creation}\n")

'''


args = parse_arguments()
simple_cache = simple_cache_entries(args.directory)
simple_cache.parse_cache_entries()
print(simple_cache.cache_files)