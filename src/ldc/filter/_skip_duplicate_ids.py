from typing import List

from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION, get_metadata
from ldc.core import LOGGING_WARN
from ldc.filter import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData


class SkipDuplicateIDs(Filter):
    """
    Suppresses records with IDs that have already passed through.
    """

    def __init__(self, logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self._ids = set()
        self._num_ids_skipped = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "skip-duplicate-ids"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Suppresses records with IDs that have already passed through. Uses the 'id' value from the meta-data."

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

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

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._ids = set()
        self._num_ids_skipped = 0

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        # get meta data
        meta = get_metadata(data)

        # get ID
        id_ = None
        if (meta is not None) and ("id" in meta):
            id_ = meta["id"]

        # already passed through?
        if id_ in self._ids:
            self._num_ids_skipped += 1
            return None
        else:
            self._ids.add(id_)
            return data

    def finalize(self):
        """
        Finishes the reading, e.g., for closing files or databases.
        """
        self.logger().info("# duplicate IDs skipped: %d" % self._num_ids_skipped)
