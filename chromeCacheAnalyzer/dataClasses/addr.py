import dataclasses
from typing import Optional
import enum


# Bitmask and offset constants
INITIALIZED_MASK = 0x80000000
FILE_TYPE_MASK = 0x70000000
FILE_TYPE_OFFSET = 28
RESERVED_BITS_MASK = 0x0c000000
NUM_BLOCKS_MASK = 0x03000000
NUM_BLOCKS_OFFSET = 24
FILE_SELECTOR_MASK = 0x00ff0000
FILE_SELECTOR_OFFSET = 16
START_BLOCK_MASK = 0x0000FFFF
FILE_NAME_MASK = 0x0FFFFFFF



class FileType(enum.IntEnum):
    EXTERNAL = 0
    RANKINGS = 1
    BLOCK_256 = 2
    BLOCK_1K = 3
    BLOCK_4K = 4
    BLOCK_FILES = 5
    BLOCK_ENTRIES = 6
    BLOCK_EVICTED = 7

    
    @property
    def is_block_file(self) -> bool:
        block_file_types = {FileType.BLOCK_256, FileType.BLOCK_1K, FileType.BLOCK_4K}
        return self in block_file_types

    
    @property
    def size(self) -> int:
        return self.value



@dataclasses.dataclass(frozen=True)
class Addr:
    is_initialized: bool
    file_type: FileType
    file_number: Optional[int] = None
    contiguous_blocks: Optional[int] = None
    file_selector: Optional[int] = None
    block_number: int = 0

    
    @classmethod
    def from_int(cls, i: int):
        is_initialized = bool(i & INITIALIZED_MASK)
        file_type = FileType((i & FILE_TYPE_MASK) >> FILE_TYPE_OFFSET)

        if file_type == FileType.EXTERNAL:
            file_number = i & FILE_NAME_MASK
            return cls(is_initialized, file_type, file_number)

        contiguous_blocks = 1 + ((i & NUM_BLOCKS_MASK) >> NUM_BLOCKS_OFFSET)
        file_selector = (i & FILE_SELECTOR_MASK) >> FILE_SELECTOR_OFFSET
        block_number = i & START_BLOCK_MASK

        return cls(is_initialized, file_type, None, contiguous_blocks, file_selector, block_number)

    
    def __repr__(self):
        return (f"<Addr: is_initialized: {self.is_initialized}; file_type: {self.file_type.name}; "
                f"file_number: {self.file_number}; contiguous_blocks: {self.contiguous_blocks}; "
                f"file_selector: {self.file_selector}; block_number: {self.block_number}>")

    
    @property
    def external_file_number(self) -> Optional[int]:
        return self.file_number if self.file_type == FileType.EXTERNAL else None
