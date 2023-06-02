import queue
import re

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


def find_elements_and_put_in_queue(queue: queue.Queue, driver: WebDriver):
    for element in driver.find_elements(By.XPATH, '//*[@id="l-searchResults"]/div/div'):
        queue.put(element)


def get_property_id(element: WebElement) -> str | None:
    if regex_search_result := re.search(
        "property-([0-9]*)", element.get_attribute("id")
    ):
        return regex_search_result.group(1)
    return None


def subpage(property_id: str) -> str:
    return f"https://www.rightmove.co.uk/properties/{ property_id }"
