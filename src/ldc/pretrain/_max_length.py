import argparse
import copy

from ldc.core import LOGGING_WARN, domain_suffix
from ._core import PretrainData, PretrainFilter
from ldc.text_utils import apply_max_length


class MaxLength(PretrainFilter):
    """
    Splits pretrain text into segments of at most the specified length (uses word boundary).
    """

    def __init__(self, max_length: int = -1, split_records: bool = False, logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param max_length: the maximum text length to allow, <= 0 for unbounded
        :type max_length: int
        :param split_records: whether to split the records
        :type split_records: bool
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.max_length = max_length
        self.split_records = split_records
        self._total_pre = 0
        self._total_post = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "max-length-" + domain_suffix(self)

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Splits pretrain text into segments of at most the specified length (uses word boundary)."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-m", "--max_length", type=int, help="The maximum text length, use <=0 for unbounded.", default=-1, required=False)
        parser.add_argument("-s", "--split_records", action="store_true", help="Splits the lines into separate records (one line per record) after reassambling the lines instead of combining them back into single document.", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.max_length = ns.max_length
        self.split_records = ns.split_records

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._total_pre = 0
        self._total_post = 0

    def _do_process(self, data: PretrainData):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data
        if self.max_length <= 0:
            return result

        lines = data.content.split("\n")
        pre = len(lines)
        lines = apply_max_length(lines, self.max_length)
        post = len(lines)
        self._total_pre += pre
        self._total_post += post
        if post == pre:
            return result
        self.logger().debug("enforcing max length %d, #lines: %d -> %d" % (self.max_length, pre, post))

        if self.split_records:
            result = []
            for line in lines:
                result.append(PretrainData(
                    content=line,
                    meta=copy.deepcopy(data.meta)
                ))
        else:
            result = PretrainData(
                content="\n".join(lines),
                meta=data.meta
            )

        return result

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.logger().info("total of enforcing max length %d, #lines: %d -> %d" % (self.max_length, self._total_pre, self._total_post))
