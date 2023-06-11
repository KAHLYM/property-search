import atexit
import json
import os
from dataclasses import asdict, dataclass

from local_logging import logger


@dataclass
class Metadata:
    command: str
    source: str

    def __init__(self, command: str, source: str):
        self.command = command
        self.source = source


class Meta:
    def __init__(self, output: str):
        self._path = os.path.join(output, "meta.json")
        self._data = {}

        if not os.path.isdir(output):
            raise ValueError("output is not a directory")

        if os.path.exists(self._path):
            with open(self._path, "r") as f:
                self._data = json.load(f)
            logger.info(f"Loaded metadata from { self._path }")

        atexit.register(self._dump_data)

    def _dump_data(self) -> None:
        if self._data:
            with open(self._path, "w") as f:
                json.dump(self._data, f)
            logger.info(f"Dumped metadata to { self._path }")

    def add(self, key: str, metadata: Metadata) -> None:
        self._data[key] = asdict(metadata)
        logger.debug(f"Added metadata for key { key }")

    def remove(self, key: str) -> None:
        self._data.pop(key, None)
        logger.debug(f"Removed metadata for key { key }")
