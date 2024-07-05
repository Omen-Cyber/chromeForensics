class BlockFileIndexFile:
# net/disk_cache/blockfile/disk_format.h

    def __init__(self, file_path: Union[os.PathLike, str]):
        self._input_path = pathlib.Path(file_path)
        with BinaryReader(self._input_path.open("rb")) as reader:
            self._header = BlockFileIndexHeader.from_reader(reader)
            self._entries = tuple(reader.read_addr() for _ in range(self._header.table_length))
            self._entries_initialized = tuple(x for x in self._entries if x.is_initialized)

    @property
    def input_path(self):
        return self._input_path

    @property
    def header(self) -> BlockFileIndexHeader:
        return self._header

    @property
    def index(self) -> Collection[Addr]:
        return self._entries

    @property
    def index_initialized_only(self):
        return self._entries_initialized