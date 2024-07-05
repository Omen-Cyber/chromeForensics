class Addr:
    # net/disk_cache/blockfile/addr.h

    def __init__(
            self, is_initialized: bool, file_type: int, file_number: Optional[int],
            contiguous_blocks: Optional[int], file_selector: Optional[int], block_number: int):
        self._is_initialized = is_initialized
        self._file_type = file_type
        self._file_number = file_number
        self._contiguous_blocks = contiguous_blocks
        self._file_selector = file_selector
        self._block_number = block_number

    def __repr__(self):
        return (f"<Addr: is_initialized: {self._is_initialized}; file_type: {self._file_type}; "
                f"file_number: {self._file_number}; contiguous_blocks: {self._contiguous_blocks}; "
                f"file_selector: {self._file_selector}; block_number: {self._block_number}>")

    @classmethod
    def from_int(cls, i: int):
        is_initialized = (i & 0x80000000) > 0
        file_type = (i & 0x70000000) >> 28

        if file_type == 0:
            file_number = i & 0x0fffffff
            contiguous_blocks = None
            file_selector = None
            block_number = None
        else:
            file_number = None
            contiguous_blocks = 1 + ((i & 0x03000000) >> 24)
            file_selector = (i & 0x00ff0000) >> 16
            block_number = i & 0x0000ffff

        return Addr(is_initialized, file_type, file_number, contiguous_blocks, file_selector, block_number)

    @property
    def is_initialized(self) -> bool:
        return self._is_initialized

    @property
    def file_type(self) -> int:
        return self._file_type

    @property
    def contiguous_blocks(self) -> int:
        return self._contiguous_blocks

    @property
    def file_selector(self) -> int:
        return self._file_selector

    @property
    def block_number(self) -> int:
        return self._block_number

    @property
    def external_file_number(self) -> int:
        return self._file_number