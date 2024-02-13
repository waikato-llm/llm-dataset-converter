import logging

from typing import List, Union

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
