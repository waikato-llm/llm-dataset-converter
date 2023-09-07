import argparse
import logging
import os

from dataclasses import dataclass
from typing import List, Union, Dict, Optional

ENV_LLM_LOGLEVEL = "LLM_LOGLEVEL"
""" environment variable for the global default logging level. """

DOMAIN_ANY = "any"
DOMAIN_PAIRS = "pairs"
DOMAIN_PRETRAIN = "pretrain"
DOMAIN_TRANSLATION = "translation"

DOMAIN_SUFFIX_LOOKUP = {
    DOMAIN_PAIRS: "pr",
    DOMAIN_PRETRAIN: "pt",
    DOMAIN_TRANSLATION: "t9n",
}

CONVERT = "llm-convert"


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

COMPARISON_LESSTHAN = "lt"
COMPARISON_LESSOREQUAL = "le"
COMPARISON_EQUAL = "eq"
COMPARISON_NOTEQUAL = "ne"
COMPARISON_GREATEROREQUAL = "ge"
COMPARISON_GREATERTHAN = "gt"
COMPARISONS = [
    COMPARISON_LESSTHAN,
    COMPARISON_LESSOREQUAL,
    COMPARISON_EQUAL,
    COMPARISON_NOTEQUAL,
    COMPARISON_GREATEROREQUAL,
    COMPARISON_GREATERTHAN,
]
COMPARISON_HELP = COMPARISON_LESSTHAN + ": less than, " \
    + COMPARISON_LESSOREQUAL + ": less or equal, " \
    + COMPARISON_EQUAL + ": equal, " \
    + COMPARISON_NOTEQUAL + ": not equal, " \
    + COMPARISON_GREATERTHAN + ": greater than, " \
    + COMPARISON_GREATEROREQUAL + ": greater of equal"


LOCATION_ANY = "any"
LOCATION_INSTRUCTION = "instruction"
LOCATION_INPUT = "input"
LOCATION_OUTPUT = "output"
LOCATION_CONTENT = "content"
LOCATIONS = [LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT]
LOCATIONS_PAIRS = [LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT]
LOCATIONS_PRETRAIN = [LOCATION_ANY, LOCATION_CONTENT]
LOCATIONS_TRANSLATION = [LOCATION_ANY, LOCATION_CONTENT]


DEFAULT_END_CHARS = ".!?;:)"
""" the default end characters for a sentence. """

DEFAULT_QUOTE_CHARS = "\"'”’"
""" the default quote characters. """


def str_to_logging_level(level: str) -> int:
    """
    Turns a logging level string into the corresponding integer constant.

    :param level: the level to convert
    :type level: str
    :return: the int level
    :rtype: int
    """
    if level not in LOGGING_LEVELS:
        raise Exception("Invalid logging level (%s): %s" % ("|".join(LOGGING_LEVELS), level))
    if level == LOGGING_CRITICAL:
        return logging.CRITICAL
    elif level == LOGGING_ERROR:
        return logging.ERROR
    elif level == LOGGING_WARN:
        return logging.WARN
    elif level == LOGGING_INFO:
        return logging.INFO
    elif level == LOGGING_DEBUG:
        return logging.DEBUG
    else:
        raise Exception("Unhandled logging level: %s" % level)


def init_logging():
    """
    Initializes the logging.
    """
    level = logging.WARNING
    if os.getenv(ENV_LLM_LOGLEVEL) is not None:
        level = str_to_logging_level(os.getenv(ENV_LLM_LOGLEVEL))
    logging.basicConfig(level=level)


def set_logging_level(logger: logging.Logger, level: str):
    """
    Sets the logging level of the logger.

    :param logger: the logger to update
    :type logger: logging.Logger
    :param level: the level string, see LOGGING_LEVELS
    :type level: str
    """
    logger.setLevel(str_to_logging_level(level))


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

    def _add_option(self, name: str, value):
        """
        Adds the key/value to the global options.

        :param name: the name of the option
        :type name: str
        :param value: the value of the option
        """
        if self.options is None:
            self.options = argparse.Namespace()
        setattr(self.options, name, value)

    def set_logging_level(self, level: str):
        """
        Sets the global logging level.

        :param level: the level
        :type level: str
        :return: itself
        :rtype: Session
        """
        self._add_option("logging_level", level)
        set_logging_level(self.logger, level)
        return self

    def set_compression(self, compression: str):
        """
        Sets the output compression for outputs.

        :param compression: the type of compression
        :type compression: str
        :return: itself
        :rtype: Session
        """
        self._add_option("compression", compression)
        return self


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
        raise NotImplementedError()

    @session.setter
    def session(self, s: Session):
        """
        Sets the session object to use.

        :param s: the session object
        :type s: Session
        """
        raise NotImplementedError()


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
        raise NotImplementedError()

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        raise NotImplementedError()

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        raise NotImplementedError()

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

    def parse_args(self, args: List[str]) -> 'CommandlineHandler':
        """
        Parses the command-line arguments.

        :param args: the arguments to parse
        :type args: list
        :return: itself
        :rtype: CommandlineHandler
        """
        parser = self._create_argparser()
        self._apply_args(parser.parse_args(args))
        return self

    def print_help(self):
        """
        Outputs the help in the console.
        """
        self._create_argparser().print_help()

    def format_help(self) -> str:
        """
        Returns the formatted help string.

        :return: the help string
        :rtype: str
        """
        return self._create_argparser().format_help()

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
        raise NotImplementedError()


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
        raise NotImplementedError()


class MetaDataHandler(object):
    """
    Mixing for classes that manage meta-data.
    """

    def has_metadata(self) -> bool:
        """
        Returns whether meta-data is present.

        :return: True if meta-data present
        :rtype: bool
        """
        raise NotImplementedError()

    def get_metadata(self) -> Optional[Dict]:
        """
        Returns the meta-data.

        :return: the meta-data, None if not available
        :rtype: dict
        """
        raise NotImplementedError()

    def set_metadata(self, metadata: Optional[Dict]):
        """
        Sets the meta-data to use.

        :param metadata: the new meta-data, can be None
        :type metadata: dict
        """
        raise NotImplementedError()


def get_metadata(o) -> Optional[Dict]:
    """
    Retrieves the meta-data from the specified object.

    :param o: the object to get the meta-data from
    :return: the meta-data, None if not available
    """
    if isinstance(o, MetaDataHandler):
        return o.get_metadata()
    if hasattr(o, "meta"):
        obj = getattr(o, "meta")
        if isinstance(obj, dict):
            return obj
    return None


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


def domain_suffix(o: Union[str, CommandlineHandler]) -> str:
    """
    Returns the suffix for the domain. See DOMAIN_SUFFIX_LOOKUP.
    Returns the domain if no lookup defined.

    :param o: commandhandler or domain to lookup the suffix for
    :return: the suffix
    :rtype: str
    """
    if isinstance(o, CommandlineHandler):
        domain = o.domains()
        if len(domain) == 0:
            raise Exception("Require one domain to determine suffix (%s)!" % str(type(o)))
        elif len(domain) > 1:
            raise Exception("Cannot determine domain suffix for multiple domains (%s)!" % str(type(o)))
        else:
            domain = domain[0]
    elif isinstance(o, str):
        domain = o
    else:
        raise Exception("Unsupported class to determine domain for: %s" % str(type(o)))

    if domain in DOMAIN_SUFFIX_LOOKUP:
        return DOMAIN_SUFFIX_LOOKUP[domain]
    else:
        return domain
