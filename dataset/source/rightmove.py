import queue
import re
import sys
from argparse import Namespace
from logging import Logger

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Rightmove:
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

        self._execute()

    def find_elements_and_put_in_queue(queue: queue.Queue, driver: WebDriver) -> None:
        for element in driver.find_elements(
            By.XPATH, '//*[@id="l-searchResults"]/div/div'
        ):
            queue.put(element)

    def get_property_id(element: WebElement) -> str | None:
        if regex_search_result := re.search(
            "property-([0-9]*)", element.get_attribute("id")
        ):
            return regex_search_result.group(1)
        return None

    def subpage(property_id: str) -> str:
        return f"https://www.rightmove.co.uk/properties/{ property_id }"

    def _execute(self):
        elements = queue.Queue()
        self._find_elements_and_put_in_queue(elements, self._driver)

        # Get inital webpage
        self._driver.get(self._args.webpage)
        self._logger.debug(f"Loaded webpage { self._args.webpage }")

        downloads = 0
        while elements.qsize() and downloads < self._args.download:
            if property_id := self._get_property_id(elements.get()):
                self._dataset.add(self._subpage(property_id), " ".join(sys.argv))
                downloads += 1
                elements.task_done()

            if not elements.qsize():
                # Load next page if available
                # N.b. find_element will raise NoSuchElementException if no element is found so use
                # find_elements which will return an empty list if no elements are found
                if next_page := self._driver.find_elements(By.XPATH, self._args.next):
                    next_page[0].click()
                    self._logger.info(
                        f"Moved to next webpage { self._driver.current_url }"
                    )
                    self._wait.until(
                        EC.presence_of_element_located((By.XPATH, self._args.next))
                    )
                    self._find_elements_and_put_in_queue(elements, self._driver)
                else:
                    self._logger.debug(f"No next page element found")
                    break
