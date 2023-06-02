"""
Script to select and download webpage from _I'm Feeling Lucky_
python .\dataset\im_feeling_lucky.py --download 50
"""
import argparse
import hashlib
import os
import pathlib
import random
import sys
import urllib

import nltk
from data import Data
from local_logging import logger
from meta import Meta, Metadata
from nltk.corpus import gutenberg
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
parser.add_argument("--download", metavar="D", type=int, help="Number of pages to download", required=True)
parser.add_argument("--log-level", metavar="L", type=int, help="Log level defined by python logging", required=False, default=20)
parser.add_argument("--output", metavar="O", type=str, help="Output directory", required=False, default=OUTPUT_DIRECTORY)
parser.add_argument("--wait", metavar="W", type=str, help="Time in seconds to wait for network", required=False, default=1)
args = parser.parse_args()
# fmt: on

logger.setLevel(args.log_level)

# Install Chrome webdriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, args.wait)

# Create output filesystem structure
pathlib.Path(os.path.join(args.output, "data")).mkdir(parents=True, exist_ok=True)

nltk.download("gutenberg")
moby_dick = set(nltk.Text(gutenberg.words("melville-moby_dick.txt")))
moby_dick = [word.lower() for word in moby_dick if len(word) > 2]


def get_random_word() -> str:
    return moby_dick[int(random.random() * len(set(moby_dick)))]


meta = Meta(args.output)

downloads = 0
while downloads < args.download:
    query = f"https://www.bing.com/search?q={ get_random_word() }+{ get_random_word() }"
    driver.get(query)
    logger.debug(f"Generated query { query }")

    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="b_results"]')))
    if elements := driver.find_elements(By.XPATH, '//*[@id="b_results"]//a[@href]'):
        url = elements[0].get_attribute("href")
        with urllib.request.urlopen(
            urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
                },
            )
        ) as response:
            logger.debug(f"Downloaded source from { url }")

            data = Data(response.read().decode())
            data_hashed = hashlib.sha256(data.strings.encode("utf-8")).hexdigest()

            with open(
                os.path.join(args.output, "data", f"{ data_hashed }.txt"),
                "wb",
            ) as f:
                f.write(bytes(data.strings, encoding="utf8"))
            logger.info(f"Saved strings from { url }")

            meta.add(data_hashed, Metadata(" ".join(sys.argv), query))

            downloads += 1

# Teardown
driver.quit()
