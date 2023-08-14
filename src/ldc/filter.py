import argparse

from typing import List, Set

from ldc.core import CommandlineHandler, InputConsumer, OutputProducer, ANY_DOMAIN


class Filter(CommandlineHandler, InputConsumer, OutputProducer):
    """
    Base class for filters.
    """

    def keep(self, data) -> bool:
        """
        Whether to keep the data record or not.

        :param data: the record to check
        :return: True if to keep
        :rtype: bool
        """
        raise NotImplemented()


class MultiFilter(Filter):
    """
    Combines multiple filters.
    """

    def __init__(self, filters: List[Filter], verbose=False):
        """
        Initialize with the specified filters.

        :param filters: the filters to use
        :type filters: list
        :param verbose: whether to be more verbose in the output
        :type verbose: bool
        """
        super().__init__(verbose=verbose)
        self.filters = filters[:]

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "multi-filter"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Combines multiple filters."

    def domains(self) -> List[str]:
        """
        Returns the domain of the handler.

        :return: the domain
        :rtype: str
        """
        return [ANY_DOMAIN]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        if len(self.filters) > 0:
            return self.filters[0].accepts()
        else:
            return list()

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        if len(self.filters) > 0:
            return self.filters[-1].accepts()
        else:
            return list()

    def keep(self, data):
        """
        Whether to keep the data record or not.

        :param data: the record to check
        :return: True if to keep
        """
        result = True
        for f in self.filters:
            if not f.keep(data):
                result = False
                break
        return result


KEYWORD_ACTION_KEEP = "keep"
KEYWORD_ACTION_DISCARD = "discard"
KEYWORD_ACTIONS = [KEYWORD_ACTION_KEEP, KEYWORD_ACTION_DISCARD]


class KeywordFilter(Filter):
    """
    Keeps or discards data records based on keyword(s).
    """

    def __init__(self, keywords=None, action=KEYWORD_ACTION_KEEP, location=None, verbose=False):
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

    def keep(self, data):
        """
        Whether to keep the data record or not.

        :param data: the record to check
        :return: True if to keep
        :rtype: bool
        """
        # prepare lookup
        words = self._to_words(data)

        # check for keywords
        found = False
        for keyword in self.keywords:
            if keyword in words:
                found = True
                break

        if self.action == KEYWORD_ACTION_KEEP:
            result = found
            info = "keeping" if result else "discarding"
        elif self.action == KEYWORD_ACTION_DISCARD:
            result = not found
            info = "discarding" if result else "keeping"
        else:
            raise Exception("Unhandled action: %s" % self.action)

        if self.verbose:
            self.logger().info("Keyword found, %s: %s" % (info, str(data)))

        return result
