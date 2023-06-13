import sys
from argparse import Namespace
from logging import Logger

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait


class Manual:
    def __init__(
        self,
        args: Namespace,
        dataset,
        driver: WebDriver,
        logger: Logger,
        source: str,
        wait: WebDriverWait,
    ):
        self._args = args
        self._dataset = dataset
        self._driver = driver
        self._logger = logger
        self._source = source
        self._wait = wait

        self._execute()

    def _execute(self):
        with open(self._source, "r") as f:
            sources = f.readlines()

        downloads = 0
        while downloads < self._args.download and downloads < len(sources):
            self._dataset.add(sources[downloads], " ".join(sys.argv), self._args.tags)
            downloads += 1
