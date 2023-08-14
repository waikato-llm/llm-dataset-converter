import argparse
import logging

from typing import List, Dict, Iterable

ALL_DOMAINS = "all domains"
PAIRS_DOMAIN = "pairs"


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


class OutputProducer(object):
    """
    Mixin for classes that generate output.
    """

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        raise NotImplemented()


class InputConsumer(object):
    """
    Mixin for classes that consume input.
    """

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        raise NotImplemented()


class Reader(CommandlineHandler, OutputProducer):
    """
    Ancestor of classes that read data.
    """

    def read(self) -> Iterable:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable
        """
        raise NotImplemented()


class Writer(CommandlineHandler, InputConsumer):
    """
    Ancestor of classes that write data.
    """
    pass


class StreamWriter(Writer):
    """
    Ancestor for classes that write data one record at a time.
    """

    def write_stream(self, data):
        """
        Saves the data one by one.

        :param data: the data to write
        """
        raise NotImplemented()


class BatchWriter(Writer):
    """
    Ancestor of classes that write data all at once.
    """

    def write_batch(self, data: Iterable):
        """
        Saves the data in one go.

        :param data: the data to write
        :type data: Iterable
        """
        raise NotImplemented()


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
        return [ALL_DOMAINS]

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


def classes_to_str(classes: List):
    """
    Turns a list of classes into a string.

    :param classes: the list of classes to convert
    :type classes: list
    :return: the generated string
    :rtype: str
    """
    classes_str = list()
    for cls in classes:
        classes_str.append(cls.__name__)
    return ", ".join(classes_str)


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
        if not isinstance(handler1, OutputProducer):
            raise Exception(handler1.name() + " is not an OutputProducer!")
        if not isinstance(handler2, InputConsumer):
            raise Exception(handler2.name() + " is not an InputConsumer!")
        classes1 = handler1.generates()
        classes2 = handler2.accepts()
        compatible = False
        for class1 in classes1:
            if class1 in classes2:
                compatible = True
                break
        if not compatible:
            raise Exception(
                "Output(s) of " + handler1.name() + " not compatible with input(s) of " + handler2.name() + ": "
                + classes_to_str(classes1) + " != " + classes_to_str(classes2))
