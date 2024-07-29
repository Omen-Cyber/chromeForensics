from dataclasses import dataclass
from dataClasses.addr import Addr
from utils.binaryReader import BinaryReader
from typing import Collection

@dataclass(frozen=True)
class LruData:
    filled: int
    sizes: Collection[int]
    heads: Collection['Addr']
    tails: Collection['Addr']
    transactions: 'Addr'
    operation: int
    operation_list: int

    @classmethod
    def from_bytes(cls, buffer: bytes):
        with BinaryReader.from_bytes(buffer) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_reader(cls, reader: 'BinaryReader'):
        reader.read_int32(), reader.read_int32()  # skip the first two int32
        filled = reader.read_int32()
        sizes = tuple(reader.read_int32() for _ in range(5))
        heads = tuple(reader.read_addr() for _ in range(5))
        tails = tuple(reader.read_addr() for _ in range(5))
        transaction = reader.read_addr()
        operation = reader.read_int32()
        operation_list = reader.read_int32()
        reader.read_int32(), reader.read_int32(), reader.read_int32(), reader.read_int32(), reader.read_int32(), reader.read_int32(), reader.read_int32()  # skip seven int32

        return cls(filled, sizes, heads, tails, transaction, operation, operation_list)