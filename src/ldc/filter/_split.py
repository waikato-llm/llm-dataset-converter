import argparse
import numpy as np

from typing import List

from ldc.core import DOMAIN_ANY, LOGGING_WARN, get_metadata, MetaDataHandler
from ldc.filter import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData


META_SPLIT = "split"
""" the key for storing the split name in the meta-data. """


class Split(Filter):
    """
    Splits the incoming records into the specified split ratios by setting the 'split' meta-data value. Also stores the split names in the current session.
    """

    def __init__(self, split_ratios: List[int] = None, split_names: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param split_ratios: the ratios for splitting the data (must some up to 100)
        :type split_ratios: list
        :param split_names: the names for the splits (will be stored in the meta-data)
        :type split_names: list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.split_ratios = split_ratios
        self.split_names = split_names
        self._schedule = None
        self._counter = 0
        self._stats = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "split"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Splits the incoming records into the specified split ratios by setting the '%s' meta-data value. Also stores the split names in the current session." % META_SPLIT

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_ANY]

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
        parser.add_argument("-r", "--split_ratios", type=int, default=None, help="The split ratios to use for generating the splits (must sum up to 100)", nargs="+")
        parser.add_argument("-n", "--split_names", type=str, default=None, help="The split names to use for the generated splits, get stored in the meta-data under the key '" + META_SPLIT + "'.", nargs="+")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.split_ratios = ns.split_ratios[:]
        self.split_names = ns.split_names[:]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.split_ratios is None:
            raise Exception("No split ratios defined!")
        if self.split_names is None:
            raise Exception("No split name defined!")
        if len(self.split_ratios) != len(self.split_names):
            raise Exception("Differing number of split ratios and names: %d != %d" % (len(self.split_ratios), len(self.split_names)))
        if sum(self.split_ratios) != 100:
            raise Exception("Split ratios must sum up to 100, but got: %d" % sum(self.split_ratios))

        # compute greatest common denominator and generate schedule
        gcd = np.gcd.reduce(np.asarray(self.split_ratios))
        self._schedule = [0] * (len(self.split_ratios) + 1)
        for i, ratio in enumerate(self.split_ratios):
            self._schedule[i + 1] = self._schedule[i] + ratio / gcd
        self._counter = 0
        self._stats = dict()

    def _output_stats(self):
        """
        Outputs the statistics.
        """
        for split in self._stats:
            self.logger().info("%s: %d" % (split, self._stats[split]))

    def process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        if self._has_input_changed(update=True):
            if self._counter > 0:
                self.logger().info("Input changed, resetting counter.")
                self._output_stats()
                self._counter = 0

        # get meta data
        meta = get_metadata(data)
        if meta is None:
            if not isinstance(data, MetaDataHandler):
                raise Exception("Cannot access meta-data for type: %s" % str(type(data)))
            else:
                meta = dict()
                data.set_metadata(meta)

        # find split according to schedule
        split = None
        for i in range(len(self.split_names)):
            if (self._counter >= self._schedule[i]) and (self._counter < self._schedule[i + 1]):
                split = self.split_names[i]

        # set split
        meta[META_SPLIT] = split

        # update counter
        self._counter += 1
        if self._counter == self._schedule[-1]:
            self._counter = 0

        # update stats
        if split not in self._stats:
            self._stats[split] = 0
        self._stats[split] += 1

        return data

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self._output_stats()
