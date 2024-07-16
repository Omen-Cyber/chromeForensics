import logging
import os
from utils.binaryReader import BinaryReader as br
from dataClasses.blockCache import blockFileIndexHeader
from dataClasses.blockFileHeader import blockFileHeader
from dataClasses.entryStore import entryStore
from dataClasses.addr import Addr, FileType
from utils.httpResponseParser import responseParser


class blockCacheFileParser:
    def __init__(self, cache_dir, output_dir, output_format):
        self.cache_dir = cache_dir
        self.output_dir = output_dir
        self.output_format = output_format
        self._block_files = {}
        self._keys = self._build_keys()
        self._index_file = None

    def new_method(self):
        return None

    def _get_block_file(self, block_file_number):
        print(f"Getting block file number {block_file_number}")
        if block_file_number in self._block_files:
            print(f"Block file number {block_file_number} already in cache")
            return self._block_files[block_file_number]

        block_file_path = os.path.join(self.cache_dir, f"data_{block_file_number}")
        with open(block_file_path, 'rb') as f:
            reader = br(f)
            header = blockFileHeader.from_reader(reader)
            print(f"Read header: {header}")
            self._block_files[block_file_number] = (header, f)
        print(f"Cached block file number {block_file_number}")
        return self._block_files[block_file_number]

    def _build_keys(self):
        print("Building keys...")
        keys = {}
        index_file_path = os.path.join(self.cache_dir, "index")
        try:
            with open(index_file_path, 'rb') as f:
                reader = br(f)
                header = blockFileIndexHeader.from_reader(reader)
                print(f"Header Index: {header}")
                keys = {}
                for addr in header.index:
                    print(f"Processing Addr: {addr}")
                    if not addr.is_initialized:
                        continue
                    try:
                        entry_data = self.get_data_for_addr(addr)
                    except ValueError as e:
                        print(f"Error getting data for Addr: {addr}. {e}")
                        continue
                    entry_store = entryStore.from_bytes(entry_data)
                    if not entry_store:
                        continue
                    if entry_store.key:
                        keys[entry_store.key] = entry_store
                    addr = entry_store.next_entry
        except IOError:
            print(f"Error reading index file: {index_file_path}")
        print("Keys built.")
        return keys

    def get_data_for_addr(self, addr: Addr):
        if not addr.is_initialized:
            raise ValueError("Addr is not initialized")

        if addr.file_type in FileType._BLOCK_FILE_FILETYPE:
            block_header, f = self._get_block_file(addr.file_selector)
            f.seek(blockFileHeader.block_header_size + (block_header.entry_size * addr.block_number))
            return f.read(block_header.entry_size * addr.contiguous_blocks)
        elif addr.file_type == FileType.EXTERNAL:
            external_file_path = os.path.join(self.cache_dir, f"f_{addr.external_file_number:06x}")
            with open(external_file_path, 'rb') as f:
                return f.read()

        raise ValueError("Unexpected file type")

    def get_metadata(self, key: str):
        entry_store = self._keys.get(key)
        if not entry_store:
            return []

        meta_data = self.get_data_for_addr(entry_store.data_addrs[0])
        return [responseParser.from_buffer(meta_data)]

    def get_cachefile(self, key: str):
        entry_store = self._keys.get(key)
        if not entry_store:
            return []

        cache_data = self.get_data_for_addr(entry_store.data_addrs[1])
        return [cache_data]

    def parse_headers_from_stream(self, stream: bytes):
        metadata = responseParser.from_buffer(stream)
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

    def close(self):
        for _, f in self._block_files.values():
            f.close()
