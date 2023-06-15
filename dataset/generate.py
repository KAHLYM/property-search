import argparse
import logging
import os
import pathlib

from core.dataset import DataSet
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from source.im_feeling_lucky import ImFeelingLucky
from source.manual import Manual
from source.pagination import Pagination
from webdriver_manager.chrome import ChromeDriverManager

OUTPUT_DIRECTORY = os.path.join(str(pathlib.Path(__file__).parent.absolute()), "output")
pathlib.Path(OUTPUT_DIRECTORY).mkdir(parents=True, exist_ok=True)

# fmt: off
# Arguments
parser = argparse.ArgumentParser(description="Crawl website and download sub pages")
parser.add_argument("--download", metavar="D", type=int, help="Number of pages to download", required=True)
parser.add_argument("--log-level", metavar="L", type=int, help="Log level defined by python logging", required=False, default=20)
parser.add_argument("--output", metavar="O", type=str, help="Output directory", required=False, default=OUTPUT_DIRECTORY)
parser.add_argument("--tags", metavar="T", nargs='+', help="Tags associated with data", required=True)
parser.add_argument("--wait", metavar="Wa", type=str, help="Time in seconds to wait for network", required=False, default=5)
subparsers = parser.add_subparsers(help="Sources", dest="command")

parser_im_feeling_lucky = subparsers.add_parser("ifl", help="I'm feeling lucky")

parser_manual = subparsers.add_parser("manual", help="Download provided webpages")
parser_manual.add_argument("--source", metavar="S", type=str, help="Line-seperated text file of webpages")

parser_pagination = subparsers.add_parser("pagination", help="Crawl paged webpages and download sub pages")
parser_pagination.add_argument("--element", metavar="E", type=str, help="X-path to element with href", required=True)
parser_pagination.add_argument("--next", metavar="N", type=str, help="X-path to next webpage", required=True)
parser_pagination.add_argument("--webpage", metavar="We", type=str, help="Initial webpage", required=True)

args = parser.parse_args()
# fmt: on

# Logging
logging_level = logging.DEBUG
logger = logging.getLogger("main")
logger.setLevel(logging_level)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging_level)
formatter = logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(args.log_level)

# Setup DataSet
dataset = DataSet(args.output, logger)

# Install Chrome webdriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, args.wait)

# Execute command
if args.command == "pagination":
    Pagination(args, dataset, driver, logger, wait)
elif args.command == "ifl":
    ImFeelingLucky(args, dataset, driver, logger, wait)
elif args.command == "manual":
    Manual(args, dataset, driver, logger, args.source, wait)

# Teardown
driver.quit()
