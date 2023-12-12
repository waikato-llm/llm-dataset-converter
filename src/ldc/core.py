import abc
import argparse
import logging
import sys
import traceback

from dataclasses import dataclass
from typing import List, Union, Dict, Optional

from seppl import Plugin
from seppl import check_compatibility as seppl_check_compatibility
from wai.logging import add_logging_level, add_logger_name, set_logging_level, LOGGING_WARNING


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


COMPARISON_LESSTHAN = "lt"
COMPARISON_LESSOREQUAL = "le"
COMPARISON_EQUAL = "eq"
COMPARISON_NOTEQUAL = "ne"
COMPARISON_GREATEROREQUAL = "ge"
COMPARISON_GREATERTHAN = "gt"
COMPARISON_CONTAINS = "contains"
COMPARISON_MATCHES = "matches"

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

COMPARISONS_EXT = COMPARISONS[:]
COMPARISONS_EXT.append(COMPARISON_CONTAINS)
COMPARISONS_EXT.append(COMPARISON_MATCHES)
COMPARISON_EXT_HELP = COMPARISON_HELP + ", " \
                      + COMPARISON_CONTAINS + ": substring match, " \
                      + COMPARISON_MATCHES + ": regexp match"

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


@dataclass
class Session:
    """
    Session object shared among reader, filter(s), writer.
    """
    options: argparse.Namespace = None
    """ global options. """

    logger: logging.Logger = logging.getLogger("llm-dataset-converter")
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
    Mixin for classes that support session objects.
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


class DomainHandler(object):
    """
    Mixin for classes that manage domains.
    """

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        raise NotImplementedError()


class CommandlineHandler(Plugin, abc.ABC):
    """
    Base class for objects handle arguments.
    """

    def __init__(self, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the handler.

        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__()
        self.logging_level = logging_level
        self.logger_name = logger_name
        self._logger = None

    def logger(self) -> logging.Logger:
        """
        Returns the logger instance to use.

        :return: the logger
        :rtype: logging.Logger
        """
        if self._logger is None:
            if (self.logger_name is not None) and (len(self.logger_name) > 0):
                logger_name = self.logger_name
            else:
                logger_name = self.name()
            self._logger = logging.getLogger(logger_name)
            set_logging_level(self._logger, self.logging_level)
        return self._logger

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        add_logging_level(parser)
        add_logger_name(parser, help_str="The custom name to use for the logger, uses the plugin name by default")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.logging_level = ns.logging_level
        self.logger_name = ns.logger_name
        self._logger = None

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


class MetaDataHandler(object):
    """
    Mixin for classes that manage meta-data.
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


def ensure_valid_domains(plugin: Plugin):
    """
    Checks whether valid domains are specified.
    Raises an exception if not valid.

    :param plugin: the handler to check
    :type plugin: CommandlineHandler
    """
    if isinstance(plugin, DomainHandler):
        domains = plugin.domains()
        if (domains is None) or (len(domains) == 0):
            raise Exception("No domain(s) specified: " + plugin.name())


def check_compatibility(plugins: List[Plugin]):
    """
    Checks whether the plugins are compatible based on domains and inputs/outputs.
    Raises an exception if not compatible.

    :param plugins: the list of plugins to check
    :type plugins: list
    """
    seppl_check_compatibility(plugins)

    if len(plugins) == 1:
        ensure_valid_domains(plugins[0])
        return

    for i in range(len(plugins) - 1):
        ensure_valid_domains(plugins[i])
        ensure_valid_domains(plugins[i + 1])


def domain_suffix(o: Union[str, CommandlineHandler]) -> str:
    """
    Returns the suffix for the domain. See DOMAIN_SUFFIX_LOOKUP.
    Returns the domain if no lookup defined.

    :param o: commandhandler or domain to lookup the suffix for
    :return: the suffix
    :rtype: str
    """
    if isinstance(o, DomainHandler):
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


def initialize_handler(handler: CommandlineHandler, handler_type: str, raise_again: bool = False) -> bool:
    """
    Initializes the commandline handler and outputs the stacktrace and help screen
    if it fails to do so. Optionally, the exception can be raised again (to propagate).

    :param handler: the handler to initialize
    :type handler: CommandlineHandler
    :param handler_type: the name of the type to use in the error message (eg "reader")
    :type handler_type: str
    :param raise_again: whether to raise the Exception again
    :type raise_again: bool
    :return: whether the initialization was successful
    :rtype: str
    """
    try:
        handler.initialize()
        return True
    except Exception as e:
        print("\nFailed to initialize %s '%s':\n" % (handler_type, handler.name()), file=sys.stderr)
        traceback.print_exc()
        print()
        handler.print_help()
        print()
        if raise_again:
            raise e
        return False


def locations_match(locations: Union[str, List[str]], required: Union[str, List[str]]) -> bool:
    """
    Checks whether at least one of locations is present in the required list.

    :param locations: the location(s) to check
    :type locations: str or list
    :param required: the required location(s)
    :return: whether there was a match
    :rtype: bool
    """
    if isinstance(locations, str):
        locations = [locations]
    if LOCATION_ANY in locations:
        return True
    if isinstance(required, str):
        required = [required]

    result = False
    for location in locations:
        if location in required:
            result = True
            break

    return result
