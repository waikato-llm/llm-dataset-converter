import argparse
from typing import List

from wai.logging import LOGGING_WARNING
from seppl import MetaDataHandler, get_metadata
from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION
from ldc.api.pretrain import PretrainData
from ldc.api.supervised.pairs import PairData
from ldc.api.translation import TranslationData
from ldc.api import Filter


class ResetIDs(Filter):
    """
    Resets the IDs in the meta-data.
    """

    def __init__(self, offset: int = 0, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param offset: the offset for the restarting of the ID counter
        :type offset: int
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.offset = offset
        self._counter = offset

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "reset-ids"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Resets the IDs in the meta-data using consecutive integer ones."

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
        parser.add_argument("-o", "--offset", type=int, help="The offset for the ID counter", default=0, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.offset = ns.offset

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._counter = self.offset

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data

        # get metadata
        meta = get_metadata(data)
        if meta is None:
            if not isinstance(data, MetaDataHandler):
                raise Exception("Cannot access meta-data for type: %s" % str(type(data)))
            else:
                meta = dict()
                data.set_metadata(meta)

        # reset ID
        self._counter += 1
        meta["id"] = self._counter

        return result
