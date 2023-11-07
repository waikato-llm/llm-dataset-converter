from typing import List

from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN
from ldc.core import LOGGING_WARN
from ldc.filter import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData


class Llama2ToPairs(Filter):
    """
    Converts llama2 pretrain records to prompt/response pairs.
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
        return "llama2-to-pairs"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Converts llama2 pretrain records to prompts/response ones. " \
               + "The 'instruction' (ie prompt) is extracted from [INST]...[/INST] " \
               + "and the 'output' (ie response) is the string that follows the [/INST]. " \
               + "Splits on </s> to generate multiple prompt/response records."

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
        return [PretrainData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PairData]

    def _do_process(self, data: PretrainData):
        """
        Processes the data record.

        :param data: the record to process
        :type data: PairData
        :return: the potentially updated record(s)
        """
        result = []

        if "</s>" in data.content:
            items = data.content.replace("</s>", "\t").split("\t")
        else:
            items = [data.content]

        for item in items:
            instruction = None
            output = None
            item = item.replace("<s>", "").replace("[INST]", "\r").replace("[/INST]", "\n")
            if ("\r" in item) and ("\n" in item):
                instruction = item[item.index("\r")+1:item.index("\n")].strip()
                output = item[item.index("\n")+1:].strip()
            if (instruction is not None) and (output is not None):
                result.append(PairData(instruction=instruction, output=output, input=None))

        if len(result) == 1:
            result = result[0]
        return result
