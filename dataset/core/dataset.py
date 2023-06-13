import os
import pathlib
from logging import Logger

from .download import Downloader
from .meta import Meta, Metadata


class DataSet:
    def __init__(self, output: str, logger: Logger):
        self._logger = logger
        self._downloader = Downloader(output, self._logger)
        self._meta = Meta(output, self._logger)

        # Create output filesystem structure
        pathlib.Path(os.path.join(output, "data")).mkdir(parents=True, exist_ok=True)

    def add(self, url: str, command: str, tags: list) -> None:
        filename = self._downloader.download(url)
        self._meta.add(filename, Metadata(command, url, tags))
