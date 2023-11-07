from typing import List

from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN
from ldc.core import LOGGING_WARN
from ldc.filter import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData


class PairsToLlama2(Filter):
    """
    Converts records of prompt/output pairs to llama2 pretrain ones.
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

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "pairs-to-llama2"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Converts records of prompt/output pairs to llama2 pretrain ones. " \
               + "The 'instruction' (ie prompt) gets wrapped in [INST]...[/INST] " \
               + "and the 'output' (ie response) follows that."

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS, DOMAIN_PRETRAIN]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PretrainData]

    def _do_process(self, data: PairData):
        """
        Processes the data record.

        :param data: the record to process
        :type data: PairData
        :return: the potentially updated record(s)
        """
        content = "<s> [INST] %s [/INST] %s </s>" % (data.instruction, data.output)
        return PretrainData(content=content)
