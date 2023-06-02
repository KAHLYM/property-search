import logging

logging_level = logging.DEBUG
logger = logging.getLogger("main")
logger.setLevel(logging_level)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging_level)
formatter = logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
