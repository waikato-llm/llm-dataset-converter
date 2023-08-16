import argparse
import logging

from dataclasses import dataclass
from typing import List

ANY_DOMAIN = "any"
PAIRS_DOMAIN = "pairs"
PRETRAIN_DOMAIN = "pretrain"

CONVERT = "llm-convert"
HUGGINGFACE_DOWNLOAD = "llm-hf-download"


LOGGING_DEBUG = "DEBUG"
LOGGING_INFO = "INFO"
LOGGING_WARN = "WARN"
LOGGING_ERROR = "ERROR"
LOGGING_CRITICAL = "CRITICAL"
LOGGING_LEVELS = [
    LOGGING_DEBUG,
    LOGGING_INFO,
    LOGGING_WARN,
    LOGGING_ERROR,
    LOGGING_CRITICAL,
]


def set_logging_level(logger: logging.Logger, level: str):
    """
    Sets the logging level of the logger.

    :param logger: the logger to update
    :type logger: logging.Logger
    :param level: the level string, see LOGGING_LEVELS
    :type level: str
    """
    if level not in LOGGING_LEVELS:
        raise Exception("Invalid logging level (%s): %s" % ("|".join(LOGGING_LEVELS), level))
    if level == LOGGING_CRITICAL:
        logger.setLevel(logging.CRITICAL)
    elif level == LOGGING_ERROR:
        logger.setLevel(logging.ERROR)
    elif level == LOGGING_WARN:
        logger.setLevel(logging.WARN)
    elif level == LOGGING_INFO:
        logger.setLevel(logging.INFO)
    elif level == LOGGING_DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        raise Exception("Unhandled logging level: %s" % level)


@dataclass
class Session:
    """
    Session object shared among reader, filter(s), writer.
    """
    options: argparse.Namespace = None
    """ global options. """

    logger: logging.Logger = logging.getLogger(CONVERT)
    """ the global logger. """

    count: int = 0
    """ the record counter. """

    current_input = None
    """ the current input etc. """

    input_changed: bool = False
    """ whether the input has changed. """


class SessionHandler(object):
    """
    Mixing for classes that support session objects.
    """

    @property
    def session(self) -> Session:
        """
        Returns the current session object

        :return: the session object
        :rtype: Session
        """
        raise NotImplemented()

    @session.setter
    def session(self, s: Session):
        """
        Sets the session object to use.

        :param s: the session object
        :type s: Session
        """
        raise NotImplemented()


class CommandlineHandler(object):
    """
    Base class for objects handle arguments.
    """

    def __init__(self, logging_level: str = LOGGING_WARN):
        """
        Initializes the handler.

        :param logging_level: the logging level to use
        :type logging_level: str
        """
        self.logging_level = logging_level
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
            set_logging_level(self._logger, self.logging_level)
        return self._logger

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = argparse.ArgumentParser(
            description=self.description(),
            prog=self.name(),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-l", "--logging_level", choices=LOGGING_LEVELS, default=LOGGING_WARN, help="The logging level to use")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        self.logging_level = ns.logging_level

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
        self.logger().info("Initializing...")

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
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
