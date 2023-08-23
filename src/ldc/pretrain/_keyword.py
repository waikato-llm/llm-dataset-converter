from typing import List, Set

from ldc.core import LOGGING_WARN
from ldc.filter import KeywordFilter, KEYWORD_ACTION_KEEP, KEYWORD_ACTION_DISCARD, KEYWORD_ACTIONS
from ldc.pretrain import PretrainFilter


LOCATION_ANY = "any"
LOCATION_CONTENT = "content"
LOCATIONS = [LOCATION_ANY, LOCATION_CONTENT]


class Keyword(KeywordFilter, PretrainFilter):
    """
    Keeps or discards data records based on keyword(s).
    """

    def __init__(self, keywords=None, action=KEYWORD_ACTION_KEEP, location=LOCATION_ANY, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param keywords: the list of keywords to look for (lower case)
        :type keywords: list
        :param action: the action to perform
        :type action: str
        :param location: in which part of the data to look for the keywords
        :type location: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(keywords=keywords, action=action, location=location, logging_level=logging_level)

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "keyword-pretrain"

    def _get_locations(self) -> List[str]:
        """
        Returns all the possible locations.

        :return: the locations
        :rtype: list
        """
        return LOCATIONS

    def _get_default_location(self) -> str:
        """
        Return the default location to use.

        :return: the location
        :rtype: str
        """
        return LOCATION_ANY

    def _to_words(self, data) -> Set[str]:
        """
        Turns the record into words.

        :return: the compiled set of words (lower case)
        :rtype: set
        """
        words = set()
        if self.location in [LOCATION_CONTENT, LOCATION_ANY]:
            words.update(data.content.lower().split())
        return words
