import datetime
import os
import re
import urllib
from logging import Logger

from .data import Data


class Downloader:
    def __init__(self, output: str, logger: Logger):
        self._logger = logger
        self._output = output

    def download(self, url: str) -> str:
        try:
            with urllib.request.urlopen(
                urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
                    },
                )
            ) as response:
                self._logger.debug(f"Downloaded source from { url.rstrip() }")

                pattern = re.compile('[\W_]+', re.UNICODE)
                filename = pattern.sub('', datetime.datetime.now().isoformat())

                data = Data(response.read().decode(), self._logger)

                with open(
                    os.path.join(self._output, "data", f"{ filename }.txt"),
                    "wb",
                ) as f:
                    f.write(bytes(data.strings, encoding="utf8"))
                self._logger.debug(f"Saved strings from { url }")

                return filename
        except Exception as e:
            self._logger.warn(f"Caught exception", e)
