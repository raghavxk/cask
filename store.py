import os.path
import time
import typing

from serializers import (
    KeyEntry,
    encode_kv,
    decode_kv,
    decode_header,
    HEADER_SIZE,
)

DEFAULT_WHENCE: typing.Final[int] = 0


class Cask:
    def __init__(self, file_name: str = "cask.db"):
        self.file_name: str = file_name
        self.write_position: int = 0
        self.key_dir: dict[str, KeyEntry] = {}

        if os.path.exists(file_name):
            self._init_key_dir()

        self.file: typing.BinaryIO = open(file_name, "a+b")

    def set(self, key: str, value: str) -> None:
        timestamp: int = int(time.time())
        sz, data = encode_kv(timestamp=timestamp, key=key, value=value)
        self._write(data)
        kv: KeyEntry = KeyEntry(
            timestamp=timestamp, position=self.write_position, total_size=sz
        )
        self.key_dir[key] = kv
        self.write_position += sz

    def get(self, key: str) -> str | None:
        kv: KeyEntry | None = self.key_dir.get(key)
        if not kv:
            return None
        self.file.seek(kv.position, DEFAULT_WHENCE)
        data: bytes = self.file.read(kv.total_size)
        _, _, value = decode_kv(data=data)
        return value

    def _write(self, data: bytes) -> None:
        self.file.write(data)
        self.file.flush()
        os.fsync(self.file.fileno())

    def _init_key_dir(self) -> None:
        print("--Initiasling the db")
        with open(self.file_name, "rb") as f:
            while header_bytes := f.read(HEADER_SIZE):
                timestamp, key_size, value_size = decode_header(data=header_bytes)
                key_bytes = f.read(key_size)
                value_bytes = f.read(value_size)
                key = key_bytes.decode("utf-8")
                value = value_bytes.decode("utf-8")
                total_size = HEADER_SIZE + key_size + value_size
                kv = KeyEntry(
                    timestamp=timestamp,
                    position=self.write_position,
                    total_size=total_size,
                )
                self.key_dir[key] = kv
                self.write_position += total_size
                print(f"loaded k = {key} value = {value}")
            print("initialisation complete")

    def close(self) -> None:
        self.file.flush()
        os.fsync(self.file.fileno())
        self.file.close()

    def __setitem__(self, key: str, value: str) -> None:
        return self.set(key, value)

    def __getitem__(self, item: str) -> str | None:
        return self.get(item)
