import argparse
import logging

from typing import List, Union, Optional

import seppl

from seppl import Plugin, get_class_name
from seppl import check_compatibility as seppl_check_compatibility


ENV_LLM_LOGLEVEL = "LLM_LOGLEVEL"
""" environment variable for the global default logging level. """

DOMAIN_ANY = "any"
DOMAIN_PAIRS = "pairs"
DOMAIN_CLASSIFICATION = "classification"
DOMAIN_PRETRAIN = "pretrain"
DOMAIN_TRANSLATION = "translation"

DOMAIN_SUFFIX_LOOKUP = {
    DOMAIN_PAIRS: "pr",
    DOMAIN_CLASSIFICATION: "cl",
    DOMAIN_PRETRAIN: "pt",
    DOMAIN_TRANSLATION: "t9n",
}

LOCATION_ANY = "any"
LOCATION_INSTRUCTION = "instruction"
LOCATION_INPUT = "input"
LOCATION_OUTPUT = "output"
LOCATION_CONTENT = "content"
LOCATION_TEXT = "text"
LOCATIONS = [LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, LOCATION_TEXT]
LOCATIONS_CLASSIFICATION = [LOCATION_ANY, LOCATION_TEXT]
LOCATIONS_PAIRS = [LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT]
LOCATIONS_PRETRAIN = [LOCATION_ANY, LOCATION_CONTENT]
LOCATIONS_TRANSLATION = [LOCATION_ANY, LOCATION_CONTENT]


DEFAULT_END_CHARS = ".!?;:)"
""" the default end characters for a sentence. """

DEFAULT_QUOTE_CHARS = "\"'”’"
""" the default quote characters. """


class Session(seppl.Session):
    """
    Session object shared among reader, filter(s), writer.
    """
    logger: logging.Logger = logging.getLogger("llm-dataset-converter")
    """ the global logger. """

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


def ensure_valid_domains(handler: DomainHandler):
    """
    Checks whether valid domains are specified.
    Raises an exception if not valid.

    :param handler: the handler to check
    :type handler: Plugin
    """
    if isinstance(handler, DomainHandler):
        domains = handler.domains()
        if (domains is None) or (len(domains) == 0):
            if isinstance(handler, Plugin):
                raise Exception("No domain(s) specified: " + handler.name())
            else:
                raise Exception("No domain(s) specified: " + get_class_name(handler))


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


def domain_suffix(o: Union[str, Plugin]) -> str:
    """
    Returns the suffix for the domain. See DOMAIN_SUFFIX_LOOKUP.
    Returns the domain if no lookup defined.

    :param o: plugin or domain to look up the suffix for
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


def add_location_argument(parser: argparse.ArgumentParser, help_str: str, default: Optional[str] = LOCATION_ANY):
    """
    Adds the location option to the parser.

    :param parser: the parser to add to
    :type parser: argparse.ArgumentParser
    :param help_str: the help string preceding the classification/pairs/etc help
    :type help_str: str
    :param default: the default location to use
    :type default: str
    """
    parser.add_argument("-L", "--location", choices=LOCATIONS, nargs="*", default=default,
                        help=help_str + "; "
                             + "classification: " + "|".join(LOCATIONS_CLASSIFICATION)
                             + ", pairs: " + "|".join(LOCATIONS_PAIRS)
                             + ", pretrain: " + "|".join(LOCATIONS_PRETRAIN)
                             + ", translation: " + "|".join(LOCATIONS_PRETRAIN))


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
