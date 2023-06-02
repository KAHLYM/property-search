"""
Script to crawl website and download sub pages
python .\dataset\rightmove_navigator.py --webpage "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E87490&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=" --next //*[@id="l-container"]/div[3]/div/div/div/div[3]/button --max-download 50
"""
import argparse
import hashlib
import os
import pathlib
import queue
import sys
import urllib

import rightmove
from data import Data
from local_logging import logger
from meta import Meta, Metadata
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

OUTPUT_DIRECTORY = os.path.join(str(pathlib.Path(__file__).parent.absolute()), "output")
pathlib.Path(OUTPUT_DIRECTORY).mkdir(parents=True, exist_ok=True)

# fmt: off
# Arguments
parser = argparse.ArgumentParser(description="Crawl website and download sub pages")
parser.add_argument("--webpage", metavar="W", type=str, help="Initial webpage", required=True)
parser.add_argument("--next", metavar="N", type=str, help="X-path to next webpage")
parser.add_argument("--max-download", metavar="MD", type=int, help="Maximum number of subpages to donwload", required=True)
parser.add_argument("--output", metavar="O", type=str, help="Output directory", required=False, default=OUTPUT_DIRECTORY)
parser.add_argument("--wait", metavar="W", type=str, help="Time in seconds to wait for network", required=False, default=1)
parser.add_argument("--log-level", metavar="L", type=int, help="Log level defined by python logging", required=False, default=20)
args = parser.parse_args()
# fmt: on

logger.setLevel(args.log_level)

# Install Chrome webdriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, args.wait)

# Get inital webpage
driver.get(args.webpage)
logger.debug(f"Loaded webpage { args.webpage }")

# Create output filesystem structure
pathlib.Path(os.path.join(args.output, "data")).mkdir(parents=True, exist_ok=True)

meta = Meta(args.output)

elements = queue.Queue()
rightmove.find_elements_and_put_in_queue(elements, driver)

downloads = 0
while elements.qsize() and downloads < args.max_download:
    if property_id := rightmove.get_property_id(elements.get()):
        subpage = rightmove.subpage(property_id)

        with urllib.request.urlopen(subpage) as response:
            logger.debug(f"Downloaded source from { subpage }")

            data = Data(response.read().decode())
            data_hashed = hashlib.sha256(data.strings.encode("utf-8")).hexdigest()

            with open(
                os.path.join(args.output, "data", f"{ data_hashed }.txt"),
                "wb",
            ) as f:
                f.write(bytes(data.strings, encoding="utf8"))
            logger.info(f"Saved strings from { subpage }")

            meta.add(data_hashed, Metadata(" ".join(sys.argv), subpage))

            downloads += 1
            elements.task_done()

    if not elements.qsize():
        # Load next page if available
        # N.b. find_element will raise NoSuchElementException if no element is found so use
        # find_elements which will return an empty list if no elements are found
        if next_page := driver.find_elements(By.XPATH, args.next):
            next_page[0].click()
            logger.info(f"Moved to next webpage { driver.current_url }")
            wait.until(EC.presence_of_element_located((By.XPATH, args.next)))
            rightmove.find_elements_and_put_in_queue(elements, driver)
        else:
            logger.debug(f"No next page element found")
            break

# Teardown
driver.quit()
