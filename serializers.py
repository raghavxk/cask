import struct
import typing

# little ending and unsigned long
HEADER_FORMAT: typing.Final[str] = "<LLL"
HEADER_SIZE: typing.Final[int] = 12


class KeyEntry:
    def __init__(self, timestamp: int, position: int, total_size: int):
        self.timestamp: int = timestamp
        self.position: int = position
        self.total_size: int = total_size


def encode_header(timestamp: int, key_size: int, value_size: int) -> bytes:
    return struct.pack(HEADER_FORMAT, timestamp, key_size, value_size)


def encode_kv(timestamp: int, key: str, value: str) -> tuple[int, bytes]:
    header: bytes = encode_header(timestamp, len(key), len(value))
    data: bytes = b"".join([str.encode(key), str.encode(value)])
    return (HEADER_SIZE + len(data), header + data)


def decode_kv(data: bytes) -> tuple[int, str, str]:
    timestamp, key_size, _ = struct.unpack(
        HEADER_FORMAT, data[:HEADER_SIZE])
    key_bytes: bytes = data[HEADER_SIZE: HEADER_SIZE + key_size]
    value_bytes: bytes = data[HEADER_SIZE + key_size:]
    key: str = key_bytes.decode("utf-8")
    value: str = value_bytes.decode("utf-8")
    return (timestamp, key, value)


def decode_header(data: bytes) -> tuple[int, int, int]:
    timestamp, key_size, value_size = struct.unpack(HEADER_FORMAT, data)
    return timestamp, key_size, value_size
