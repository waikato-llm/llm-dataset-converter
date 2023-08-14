from typing import List, Set

from ldc.filter import KeywordFilter, KEYWORD_ACTION_KEEP
from ldc.supervised.pairs import PairFilter


LOCATION_ANY = "any"
LOCATION_INSTRUCTION = "instruction"
LOCATION_INPUT = "input"
LOCATION_OUTPUT = "output"
LOCATIONS = [LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT]


class Keyword(KeywordFilter, PairFilter):
    """
    Keeps or discards data records based on keyword(s).
    """

    def __init__(self, keywords=None, action=KEYWORD_ACTION_KEEP, location=LOCATION_ANY, verbose=False):
        """
        Initializes the filter.

        :param keywords: the list of keywords to look for (lower case)
        :type keywords: list
        :param action: the action to perform
        :type action: str
        :param location: in which part of the data to look for the keywords
        :type location: str
        :param verbose: whether to be more verbose in the output
        :type verbose: bool
        """
        super().__init__(keywords=keywords, action=action, location=location, verbose=verbose)

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "pairs-keyword"

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
        if self.location in [LOCATION_INSTRUCTION, LOCATION_ANY]:
            words.update(data.instruction.lower().split())
        if self.location in [LOCATION_INPUT, LOCATION_ANY]:
            words.update(data.input.lower().split())
        if self.location in [LOCATION_OUTPUT, LOCATION_ANY]:
            words.update(data.output.lower().split())
        return words
