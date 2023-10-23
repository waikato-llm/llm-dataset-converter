import argparse
import re
from typing import List, Tuple

from ldc.core import LOGGING_WARN, DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION
from ldc.core import COMPARISONS_EXT, COMPARISON_LESSTHAN, COMPARISON_LESSOREQUAL, COMPARISON_EQUAL, COMPARISON_NOTEQUAL, \
    COMPARISON_GREATEROREQUAL, COMPARISON_GREATERTHAN, COMPARISON_CONTAINS, COMPARISON_MATCHES, COMPARISON_EXT_HELP
from ldc.filter import Filter, FILTER_ACTIONS, FILTER_ACTION_KEEP, FILTER_ACTION_DISCARD
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData


class MetaData(Filter):
    """
    Keeps or discards data records based on meta-data values.
    """

    def __init__(self, field: str = None, action: str = FILTER_ACTION_KEEP,
                 comparison: str = COMPARISON_EQUAL, value=None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param field: the name of the meta-data field to perform the comparison on
        :type field: str
        :param action: the action to perform
        :type action: str
        :param comparison: the comparison to perform
        :type comparison: str
        :param value: the value to compare with
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)

        if action not in FILTER_ACTIONS:
            raise Exception("Invalid action: %s" % action)
        if comparison not in COMPARISONS_EXT:
            raise Exception("Invalid comparison: %s" % comparison)

        self.field = field
        self.value = value
        self.comparison = comparison
        self.action = action
        self.kept = 0
        self.discarded = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "metadata"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Keeps or discards data records based on meta-data comparisons. " \
               + "Performs the following comparison: METADATA_VALUE COMPARISON VALUE. " \
               + "Records that do not have the required field get discarded automatically."

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-f", "--field", type=str, help="The meta-data field to use in the comparison", required=True)
        parser.add_argument("-v", "--value", type=str, help="The value to use in the comparison", required=True)
        parser.add_argument("-c", "--comparison", choices=COMPARISONS_EXT, default=COMPARISON_EQUAL, help="How to compare the value with the meta-data value; " + COMPARISON_EXT_HELP
                            + "; in case of '" + COMPARISON_CONTAINS + "' and '" + COMPARISON_MATCHES + "' the supplied value represents the substring to find/regexp to search with")
        parser.add_argument("-a", "--action", choices=FILTER_ACTIONS, default=FILTER_ACTION_KEEP, help="How to react when a keyword is encountered")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.field = ns.field
        self.value = ns.value
        self.comparison = ns.comparison
        self.action = ns.action

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.field is None:
            raise Exception("No meta-data field provided!")
        if self.value is None:
            raise Exception("No value provided to compare with!")
        self.kept = 0
        self.discarded = 0

    def _ensure_same_type(self, v1, v2) -> Tuple:
        """
        Ensures that both values are of the same type.

        :param v1: the first value
        :param v2: the second value
        :return: the tuple of the updated values
        :rtype: tuple
        """
        if isinstance(v1, float):
            v2 = float(v2)
        elif isinstance(v1, int):
            v2 = int(v2)
        elif isinstance(v1, bool):
            v2 = str(v2).lower() == 'true'
        return v1, v2

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data

        if isinstance(data, PairData):
            meta = data.meta
        elif isinstance(data, PretrainData):
            meta = data.meta
        elif isinstance(data, TranslationData):
            meta = data.meta
        else:
            raise Exception("Unhandled type of data: %s" % str(type(data)))

        # no meta-data -> reject
        if meta is None:
            self.logger().info("No meta-data, discarded")
            self.discarded += 1
            return None

        # key not present -> reject
        if self.field not in meta:
            self.logger().info("Field '%s' not meta-data, discarded" % self.field)
            self.discarded += 1
            return None

        v1 = meta[self.field]
        v2 = self.value
        if self.comparison in [COMPARISON_CONTAINS, COMPARISON_MATCHES]:
            v1 = str(v1)
        else:
            v1, v2 = self._ensure_same_type(v1, v2)

        # compare
        if self.comparison == COMPARISON_LESSTHAN:
            comp_result = v1 < v2
        elif self.comparison == COMPARISON_LESSOREQUAL:
            comp_result = v1 <= v2
        elif self.comparison == COMPARISON_EQUAL:
            comp_result = v1 == v2
        elif self.comparison == COMPARISON_NOTEQUAL:
            comp_result = v1 != v2
        elif self.comparison == COMPARISON_GREATERTHAN:
            comp_result = v1 > v2
        elif self.comparison == COMPARISON_GREATEROREQUAL:
            comp_result = v1 >= v2
        elif self.comparison == COMPARISON_CONTAINS:
            comp_result = v2 in v1
        elif self.comparison == COMPARISON_MATCHES:
            comp_result = re.search(v2, v1) is not None
        else:
            raise Exception("Unhandled comparison: %s" % self.comparison)

        if self.action == FILTER_ACTION_KEEP:
            if not comp_result:
                result = None
        elif self.action == FILTER_ACTION_DISCARD:
            if comp_result:
                result = None
        else:
            raise Exception("Unhandled action: %s" % self.action)

        if result is None:
            self.discarded += 1
        else:
            self.kept += 1

        info = "keeping" if (result is not None) else "discarding"
        comp = str(meta[self.field] + " " + self.comparison + " " + str(self.value) + " = " + str(comp_result))
        self.logger().debug("Comparison result '%s': %s" % (comp, info))

        return result

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.logger().info("# kept: %d" % self.kept)
        self.logger().info("# discarded: %d" % self.discarded)
