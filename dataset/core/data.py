from logging import Logger

from bs4 import BeautifulSoup
from bs4.element import Comment


class Data:
    def __init__(self, data: str, logger: Logger):
        self._data = data
        self._logger = logger
        self.strings = self._extract_strings()

    def __str__(self) -> str:
        return self.strings.encode("utf-8")

    def _is_visible_tag(self, element) -> bool:
        if element.parent.name in [
            "style",
            "script",
            "head",
            "title",
            "meta",
            "[document]",
        ]:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def _extract_strings(self) -> str:
        soup = BeautifulSoup(self._data, "html.parser")
        strings = soup.findAll(string=True)
        visible_strings = filter(self._is_visible_tag, strings)
        self._logger.debug(f"Extracted and filtered { len(strings) } strings")

        # Space-seperated string with no other whitespace
        return " ".join(
            [
                string
                for string in [
                    " ".join(visible_string.split())
                    for visible_string in visible_strings
                ]
                if string
            ]
        )
