import argparse
import copy
from typing import List, Optional

from wai.logging import LOGGING_WARNING
from ldc.core import DOMAIN_PAIRS
from ._core import PairData, PAIRDATA_INSTRUCTION, PAIRDATA_INPUT, PAIRDATA_OUTPUT, PairFilter


PH_START = "{"
PH_END = "}"
PH_INSTRUCTION = PH_START + PAIRDATA_INSTRUCTION + PH_END
PH_INPUT = PH_START + PAIRDATA_INPUT + PH_END
PH_OUTPUT = PH_START + PAIRDATA_OUTPUT + PH_END


class UpdatePairData(PairFilter):
    """
    Updates the PairData according to the format strings.
    """

    def __init__(self, format_instruction: str = None, format_input: str = None, format_output: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param format_instruction: the new instruction content, use PH_INSTRUCTION to keep current
        :type format_instruction: str
        :param format_input: the new input content, use PH_INPUT to keep current
        :type format_input: str
        :param format_output: the new output content, use PH_OUTPUT to keep current
        :type format_output: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.format_instruction = format_instruction
        self.format_input = format_input
        self.format_output = format_output

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "update-pair-data"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Updates the pair data according to the format strings, allowing for tweaking or rearranging of the data."

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS]

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
        return [PairData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("--format_instruction", type=str, default=None, help="The format for the instruction content, use placeholder " + PH_INSTRUCTION + " for current value.", required=False)
        parser.add_argument("--format_input", type=str, default=None, help="The format for the input content, use placeholder " + PH_INPUT + " for current value.", required=False)
        parser.add_argument("--format_output", type=str, default=None, help="The format for the output content, use placeholder " + PH_OUTPUT + " for current value.", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.format_instruction = ns.format_instruction
        self.format_input = ns.format_input
        self.format_output = ns.format_output

    def _replace_placeholders(self, data: PairData, format_string: Optional[str]) -> Optional[str]:
        """
        Replaces the placeholders in the format string with the values of the
        supplied record and returns the updated string.

        :param data: the record to use for the placeholders
        :type data: PairData
        :param format_string: the format string to apply, ignored if empty
        :type format_string: str
        :return:
        """
        if format_string is None:
            return None
        _instruction = "" if (data.instruction is None) else data.instruction
        _input = "" if (data.input is None) else data.input
        _output = "" if (data.output is None) else data.output
        result = format_string
        if PH_START in result:
            result = result.replace(PH_INSTRUCTION, _instruction)
        if PH_START in result:
            result = result.replace(PH_INPUT, _input)
        if PH_START in result:
            result = result.replace(PH_OUTPUT, _output)
        return result

    def _do_process(self, data: PairData):
        """
        Processes the data record.

        :param data: the record to process
        :type data: PairData
        :return: the potentially updated record or None if to drop
        """
        _instruction = self._replace_placeholders(data, self.format_instruction)
        _input = self._replace_placeholders(data, self.format_input)
        _output = self._replace_placeholders(data, self.format_output)
        _meta = None if (data.meta is None) else copy.deepcopy(data.meta)
        return PairData(instruction=_instruction, input=_input, output=_output, meta=_meta)
