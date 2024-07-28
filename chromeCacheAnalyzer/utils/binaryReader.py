import io
from io import BytesIO
import struct
from typing import Union, BinaryIO
import datetime


def decode_chrome_time(chrome_time: int) -> datetime.datetime:
    """Convert Chrome's timestamp format to Python datetime."""
    epoch_start = datetime.datetime(1601, 1, 1)
    return epoch_start + datetime.timedelta(microseconds=chrome_time)


class BinaryReader:
    
    def __init__(self, stream: Union[BinaryIO, bytes]):
        if isinstance(stream, bytes):
            self.b_stream = io.BytesIO(stream)
        else:
            self.b_stream = stream
        self._closed = False

    @classmethod
    def from_bytes(cls, buffer: bytes):
        return cls(buffer)

    def tell(self):
        return self.b_stream.tell()

    def seek(self, offset, whence=io.SEEK_SET):
        return self.b_stream.seek(offset, whence)

    def read_raw(self, count):
        start_offset = self.b_stream.tell()
        result = self.b_stream.read(count)
        if len(result) != count:
            raise ValueError(
                f"Could not read all of the data starting at {start_offset}. Expected: {count}; got {len(result)}")
        return result

    def read_utf8(self, count: int) -> str:
        return self.read_raw(count).decode("utf-8")

    def read_int16(self) -> int:
        raw = self.read_raw(2)
        return struct.unpack("<h", raw)[0]

    def read_int32(self) -> int:
        raw = self.read_raw(4)
        return struct.unpack("<i", raw)[0]

    def read_int64(self) -> int:
        raw = self.read_raw(8)
        return struct.unpack("<q", raw)[0]

    def read_uint16(self) -> int:
        raw = self.read_raw(2)
        return struct.unpack("<H", raw)[0]

    def read_uint32(self) -> int:
        raw = self.read_raw(4)
        return struct.unpack("<I", raw)[0]

    def read_uint64(self) -> int:
        raw = self.read_raw(8)
        return struct.unpack("<Q", raw)[0]

    def read_addr(self) -> "Addr":
        return Addr.from_int(self.read_uint32())

    def read_datetime(self) -> datetime.datetime:
        return decode_chrome_time(self.read_uint64())

    @property
    def is_closed(self) -> bool:
        return self._closed
