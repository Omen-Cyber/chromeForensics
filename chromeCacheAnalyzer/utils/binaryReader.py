class BinaryReader:
    def __init__(self, stream: typing.BinaryIO):
        self._stream = stream
        self._closed = False

    @classmethod
    def from_bytes(cls, buffer: bytes):
        return cls(io.BytesIO(buffer))

    def close(self):
        self._stream.close()
        self._closed = True

    def __enter__(self) -> "BinaryReader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def tell(self) -> int:
        return self._stream.tell()

    def seek(self, offset: int, whence: int) -> int:
        return self._stream.seek(offset, whence)

    # if this throws an error check offset pointers, more than likey its not reading the right data
    def read_raw(self, count: int) -> bytes:
        start_offset = self._stream.tell()
        result = self._stream.read(count)
        if len(result) != count:
            raise ValueError(
                f"Could not read all of the data starting at {start_offset}. Expected: {count}; got {len(result)}")
        return result

    def read_utf8(self, count: int) -> str:
        return self.read_raw(count).decode("utf-8")  # reads a specified number of bytes (count) from the stream and decodes them as a UTF-8 string

    def read_int16(self) -> int:
        raw = self.read_raw(2)
        return struct.unpack("<h", raw)[0]  # reads 2 bytes from the stream and interprets them as a little-endian 16-bit signed integer

    def read_int32(self) -> int:
        raw = self.read_raw(4)
        return struct.unpack("<i", raw)[0]  # reads 4 bytes from the stream and interprets them as a little-endian 32-bit signed integer

    def read_int64(self) -> int:
        raw = self.read_raw(8)
        return struct.unpack("<q", raw)[0]  # reads 8 bytes from the stream and interprets them as a little-endian 64-bit signed integer

    def read_uint16(self) -> int:
        raw = self.read_raw(2)
        return struct.unpack("<H", raw)[0]  # reads 2 bytes from the stream and interprets them as a  little-endian 16-bit unsigned integer

    def read_uint32(self) -> int:
        raw = self.read_raw(4)
        return struct.unpack("<I", raw)[0]  # reads 4 bytes from the stream and interprets them as a little-endian 32-bit unsigned integer

    def read_uint64(self) -> int:
        raw = self.read_raw(8)
        return struct.unpack("<Q", raw)[0]  # reads 8 bytes from the stream and interprets them as a little-endian 64-bit unsigned integer

    def read_addr(self) -> "Addr":
        return Addr.from_int(self.read_uint32())  # calls self.read_uint32(), reads 4 bytes as 32-bit unsigned integers, then creates an Addr obj

    def read_datetime(self) -> datetime:
        return decode_chrome_time(self.read_uint64()) # reads 8 bytes from the stream, as 64-bit integers and coverts them to datetime objects

    @property
    def is_closed(self) -> bool:
        return self._closed  # closes stream
