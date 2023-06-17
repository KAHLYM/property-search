import queue
import sys
from argparse import Namespace
from logging import Logger

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Pagination:
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

        self._elements = queue.Queue()

        self._execute()

    def _find_elements_and_put_in_queue(self) -> None:
        for element in self._driver.find_elements(By.XPATH, str(self._args.element)):
            self._elements.put(element.get_attribute("href"))

    def _execute(self):
        
        # Get inital webpage
        self._driver.get(self._args.webpage)
        self._logger.debug(f"Loaded webpage { self._args.webpage }")

        self._find_elements_and_put_in_queue()

        downloads = 0
        while self._elements.qsize() and downloads < self._args.download:
            self._dataset.add(self._elements.get(), " ".join(sys.argv), self._args.tags)
            downloads += 1
            self._elements.task_done()

            if not self._elements.qsize():
                # Load next page if available
                # N.b. find_element will raise NoSuchElementException if no element is found so use
                # find_elements which will return an empty list if no elements are found
                if next_page := self._driver.find_elements(By.XPATH, self._args.next):
                    next_page[0].click() if next_page[0].tag_name == "button" else self._driver.get(next_page[0].get_attribute("href"))
                    self._logger.info(
                        f"Moved to next webpage { self._driver.current_url }"
                    )
                    self._wait.until(
                        EC.presence_of_element_located((By.XPATH, self._args.next))
                    )
                    self._find_elements_and_put_in_queue()
                else:
                    self._logger.debug(f"No next page element found")
                    break
