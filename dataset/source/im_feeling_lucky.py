import random
import sys
from argparse import Namespace
from logging import Logger

import nltk
from nltk.corpus import gutenberg
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class ImFeelingLucky:
    def __init__(
        self,
        args: Namespace,
        dataset,
        driver: WebDriver,
        logger: Logger,
        wait: WebDriverWait,
    ):
        self._args = args
        self._dataset = dataset
        self._driver = driver
        self._logger = logger
        self._wait = wait

        # TODO Check if download exists
        nltk.download("gutenberg")
        moby_dick = set(nltk.Text(gutenberg.words("melville-moby_dick.txt")))
        self._moby_dick = [word.lower() for word in moby_dick if len(word) > 2]

        self._execute()

    def _get_random_word(self) -> str:
        return self._moby_dick[int(random.random() * len(set(self._moby_dick)))]

    def _execute(self):
        downloads = 0
        while downloads < self._args.download:
            query = f"https://www.bing.com/search?q={ self._get_random_word() }+{ self._get_random_word() }"
            self._driver.get(query)
            self._logger.debug(f"Generated query { query }")

            self._wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="b_results"]'))
            )
            if elements := self._driver.find_elements(
                By.XPATH, '//*[@id="b_results"]//a[@href]'
            ):
                self._dataset.add(elements[0].get_attribute("href"), " ".join(sys.argv))
                downloads += 1
