import argparse
import logging

from typing import List, Dict, Iterable

ALL_DOMAINS = "all domains"
PAIRS_DOMAIN = "supervised/pairs"


class CommandlineHandler(object):
    """
    Base class for objects handle arguments.
    """

    def __init__(self, verbose=False):
        """
        Initializes the handler.

        :param verbose: whether to be more verbose in the output
        :type verbose: bool
        """
        self.verbose = verbose
        self._logger = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        raise NotImplemented()

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        raise NotImplemented()

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        raise NotImplemented()

    def logger(self) -> logging.Logger:
        """
        Returns the logger instance to use.

        :return: the logger
        :rtype: logging.Logger
        """
        if self._logger is None:
            self._logger = logging.getLogger(self.name())
            self._logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        return self._logger

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = argparse.ArgumentParser(
            description=self.description() + "\nDomain(s): " + "|".join(self.domains()),
            prog=self.name(),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-v", "--verbose", action="store_true", help="Whether to be more verbose with the output")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        self.verbose = ns.verbose

    def parse_args(self, args: List[str]):
        """
        Parses the command-line arguments.

        :param args: the arguments to parse
        :type args: list
        """
        parser = self._create_argparser()
        self._apply_args(parser.parse_args(args))

    def print_help(self):
        """
        Outputs the help in the console.
        """
        self._create_argparser().print_help()

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        if self.verbose:
            self.logger().info("Initializing...")

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        if self.verbose:
            self.logger().info("Finalizing...")


class Reader(CommandlineHandler):

    def read(self) -> Iterable:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable
        """
        raise NotImplemented()


class Writer(CommandlineHandler):
    pass


class StreamWriter(Writer):

    def write_stream(self, data):
        """
        Saves the data one by one.

        :param data: the data to write
        """
        raise NotImplemented()


class BatchWriter(Writer):

    def write_batch(self, data: Iterable):
        """
        Saves the data in one go.

        :param data: the data to write
        :type data: Iterable
        """
        raise NotImplemented()


class Filter(CommandlineHandler):
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
        return [ALL_DOMAINS]

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


def split_args(args: List[str], handlers: List[str]) -> Dict[str, List[str]]:
    """
    Splits the command-line arguments into handler and their associated arguments.
    Special entry "" is used for global options.

    :param args: the command-line arguments to split
    :type args: list
    :param handlers: the list of valid handler names
    :type handlers: list
    :return: the dictionary for handler name / options list
    :rtype: dict
    """
    handlers = set(handlers)
    result = dict()
    last_handler = ""
    last_args = []

    for arg in args:
        if arg in handlers:
            result[last_handler] = last_args
            last_handler = arg
            last_args = []
            continue
        else:
            last_args.append(arg)

    if last_handler is not None:
        result[last_handler] = last_args

    return result


def is_help_requested(args: List[str]):
    """
    Checks whether help was requested.

    :param args: the arguments to check
    :type args: list
    :return: True if help requested
    :rtype: bool
    """
    result = False
    for arg in args:
        if (arg == "-h") or (arg == "--help"):
            result = True
            break
    return result


def ensure_valid_domains(handler: CommandlineHandler):
    """
    Checks whether valid domains are specified.
    Raises an exception if not valid.

    :param handler: the handler to check
    :type handler: CommandlineHandler
    """
    domains = handler.domains()
    if (domains is None) or (len(domains) == 0):
        raise Exception("No domain(s) specified: " + handler.name())


def check_compatibility(handlers: List[CommandlineHandler]):
    """
    Checks whether the handlers are compatible based on their domains.
    Raises an exception if not compatible.

    :param handlers: the handlers to check
    :type handlers: CommandlineHandler
    """
    if len(handlers) == 0:
        return

    if len(handlers) == 1:
        ensure_valid_domains(handlers[0])
        return

    for i in range(len(handlers) - 1):
        handler1 = handlers[i]
        handler2 = handlers[i + 1]
        ensure_valid_domains(handler1)
        ensure_valid_domains(handler2)
        domains1 = handler1.domains()
        domains2 = handler2.domains()
        if (ALL_DOMAINS in domains1) or (ALL_DOMAINS in domains2):
            continue
        compatible = False
        for domain1 in domains1:
            if domain1 in domains2:
                compatible = True
        if not compatible:
            raise Exception(
                "Domain(s) of " + handler1.name() + " not compatible with " + handler2.name() + ": "
                + str(domains1) + " != " + str(domains2))
