import argparse
from typing import List, Set

from ldc.filter._core import Filter

KEYWORD_ACTION_KEEP = "keep"
KEYWORD_ACTION_DISCARD = "discard"
KEYWORD_ACTIONS = [KEYWORD_ACTION_KEEP, KEYWORD_ACTION_DISCARD]


class KeywordFilter(Filter):
    """
    Keeps or discards data records based on keyword(s).
    """

    def __init__(self, keywords: List[str] = None, action: str = KEYWORD_ACTION_KEEP,
                 location: str = None, verbose: bool = False):
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
        super().__init__(verbose=verbose)

        if action not in KEYWORD_ACTIONS:
            raise Exception("Invalid action: %s" % action)
        if location not in self._get_locations():
            raise Exception("Invalid location: %s" % location)

        self.keywords = keywords
        self.action = action
        self.location = location

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Keeps or discards data records based on keyword(s)."

    def _get_locations(self) -> List[str]:
        """
        Returns all the possible locations.

        :return: the locations
        :rtype: list
        """
        raise NotImplemented()

    def _get_default_location(self) -> str:
        """
        Return the default location to use.

        :return: the location
        :rtype: str
        """
        raise NotImplemented()

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-k", "--keyword", type=str, help="The keywords to look for", required=True, nargs="+")
        parser.add_argument("-l", "--location", choices=self._get_locations(), default=self._get_default_location(), help="Where to look for the keywords")
        parser.add_argument("-a", "--action", choices=KEYWORD_ACTIONS, default=KEYWORD_ACTION_KEEP, help="How to react when a keyword is encountered")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.keywords = ns.keyword[:]
        self.action = ns.action
        self.location = ns.location

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        if (self.keywords is None) or (len(self.keywords) == 0):
            raise Exception("No keywords provided!")
        self.keywords = [x.lower() for x in self.keywords]

    def _to_words(self, data) -> Set[str]:
        """
        Turns the record into words.

        :return: the compiled set of words (lower case)
        :rtype: set
        """
        raise NotImplemented()

    def process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data

        # prepare lookup
        words = self._to_words(data)

        # check for keywords
        found = False
        for keyword in self.keywords:
            if keyword in words:
                found = True
                break

        if self.action == KEYWORD_ACTION_KEEP:
            if not found:
                result = None
            info = "keeping" if result else "discarding"
        elif self.action == KEYWORD_ACTION_DISCARD:
            if found:
                result = None
            info = "discarding" if result else "keeping"
        else:
            raise Exception("Unhandled action: %s" % self.action)

        if self.verbose:
            self.logger().info("Keyword found, %s: %s" % (info, str(data)))

        return result
