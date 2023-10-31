import argparse
from typing import List

from ldc.core import LOGGING_WARN, DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION, get_metadata, MetaDataHandler
from ._core import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData


class RecordWindow(Filter):
    """
    Only lets records pass that match the defined window and step size.
    """

    def __init__(self, from_index: int = None, to_index: int = None, step: int = 1, logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param from_index: the lower bound for the window (1-based, included), ignored if None
        :type from_index: int
        :param to_index: the upper bound for the window (1-based, included), ignored if None
        :type to_index: int
        :param step: the increment to use (at least 1)
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.from_index = from_index
        self.to_index = to_index
        self.step = step
        self._counter = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "record-window"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Only lets records pass that match the defined window and step size."

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
        parser.add_argument("-f", "--from_index", type=int, help="The 1-based lower bound of the window, ignored if not supplied.", default=None, required=False)
        parser.add_argument("-t", "--to_index", type=int, help="The 1-based upper bound of the window, ignored if not supplied.", default=None, required=False)
        parser.add_argument("-s", "--step", type=int, help="The increment to use (at least 1).", default=1, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.from_index = ns.from_index
        self.to_index = ns.to_index
        self.step = ns.step

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._counter = 0
        if self.from_index is not None:
            if self.from_index < 1:
                raise Exception("From index must be at least 1, provided: %d" % self.from_index)
        if self.to_index is not None:
            if self.to_index < 1:
                raise Exception("To index must be at least 1, provided: %d" % self.to_index)
        if (self.from_index is not None) and (self.to_index is not None):
            if self.to_index < self.from_index:
                raise Exception("To index cannot be smaller than from index: from=%d to=%d" % (self.from_index, self.to_index))
        if self.step < 1:
            raise Exception("Step must be at least 1, provided: %d" % self.step)

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data

        self._counter += 1

        keep = True
        if self.from_index is not None:
            if self._counter < self.from_index:
                keep = False
        if self.to_index is not None:
            if self._counter > self.to_index:
                keep = False
        if self.step > 1:
            min_ = 1 if (self.from_index is None) else self.from_index
            if (self._counter - min_) % self.step > 0:
                keep = False

        self.logger().debug("from=%s to=%s step=%s counter=%s -> %s"
                            % (str(self.from_index), str(self.to_index), str(self.step), str(self._counter), str(keep)))

        if not keep:
            result = None

        return result
