class KeyDir:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        self.data[key] = value

    def get(self, key) -> str | None:
        return self.data.get(key)

    def close(self):
        return
