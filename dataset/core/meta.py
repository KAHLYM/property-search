import atexit
import json
import os
from dataclasses import asdict, dataclass
from logging import Logger


@dataclass
class Metadata:
    command: str
    source: str
    tags: list

    def __init__(self, command: str, source: str, tags: list):
        self.command = command
        self.source = source
        self.tags = tags


class Meta:
    def __init__(self, output: str, logger: Logger):
        self._path = os.path.join(output, "meta.json")
        self._logger = logger

        self._data = {}

        if not os.path.isdir(output):
            raise ValueError("output is not a directory")

        if os.path.exists(self._path):
            with open(self._path, "r") as f:
                self._data = json.load(f)
            self._logger.info(f"Loaded metadata from { self._path }")

        atexit.register(self._dump_data)

    def _dump_data(self) -> None:
        if self._data:
            with open(self._path, "w") as f:
                json.dump(self._data, f)
            self._logger.info(f"Dumped { len(self._data) } metadata to { self._path }")

    def add(self, key: str, metadata: Metadata) -> None:
        self._data[key] = asdict(metadata)
        self._logger.debug(f"Added metadata for key { key }")

    def remove(self, key: str) -> None:
        self._data.pop(key, None)
        self._logger.debug(f"Removed metadata for key { key }")
