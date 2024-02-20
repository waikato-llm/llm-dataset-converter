import argparse
import json
from typing import Iterable, List, Union

from wai.logging import LOGGING_WARNING
from seppl.io import locate_files
from ldc.base_io import open_file, generate_output
from ldc.api.supervised.pairs import PairData, PairReader, BatchPairWriter


class XTunerReader(PairReader):
    """
    Reader for the XTuner JSON format.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 att_instruction: str = None, att_input: str = None, att_output: str = None,
                 encoding: str = None, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param att_instruction: the attribute with the instruction data
        :type att_instruction: str
        :param att_input: the attribute with the input data
        :type att_input: str
        :param att_output: the attribute with the output data
        :type att_output: str
        :param encoding: the encoding to use, None for auto-detect
        :type encoding: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.source = source
        self.source_list = source_list
        self.att_instruction = att_instruction
        self.att_input = att_input
        self.att_output = att_output
        self.encoding = encoding
        self._inputs = None
        self._current_input = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-xtuner"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Reads single-turn conversations in XTuner JSON format (https://github.com/InternLM/xtuner/blob/v0.1.13/docs/en/user_guides/dataset_format.md#single-turn-dialogue-dataset-format)."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the XTuner file(s) to read; glob syntax is supported", required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the data files to use", required=False, nargs="*")
        parser.add_argument("--att_instruction", metavar="ATT", type=str, default=None, help="The attribute with the instructions", required=False)
        parser.add_argument("--att_input", metavar="ATT", type=str, default=None, help="The attribute with the inputs", required=False)
        parser.add_argument("--att_output", metavar="ATT", type=str, default=None, help="The attribute with the outputs", required=False)
        parser.add_argument("--encoding", metavar="ENC", type=str, default=None, help="The encoding to force instead of auto-detecting it, e.g., 'utf-8'", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.source = ns.input
        self.source_list = ns.input_list
        self.att_instruction = ns.att_instruction
        self.att_input = ns.att_input
        self.att_output = ns.att_output
        self.encoding = ns.encoding

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True)
        if self.att_instruction is None:
            self.att_instruction = "system"
        if self.att_input is None:
            self.att_input = "input"
        if self.att_output is None:
            self.att_output = "output"

    def read(self) -> Iterable[PairData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: PairData
        """
        self.finalize()

        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_input = open_file(self._current_input, mode="rt", encoding=self.encoding, logger=self.logger())

        array = json.load(self._current_input)
        for item in array:
            if "conversation" in item:
                conversation = item["conversation"]
                _instruction = None
                _input = None
                _output = None
                if self.att_instruction in conversation:
                    _instruction = conversation[self.att_instruction]
                if self.att_input in conversation:
                    _input = conversation[self.att_input]
                if self.att_output in conversation:
                    _output = conversation[self.att_output]
                yield PairData(instruction=_instruction, input=_input, output=_output)

    def has_finished(self) -> bool:
        """
        Returns whether reading has finished.

        :return: True if finished
        :rtype: bool
        """
        return len(self._inputs) == 0

    def finalize(self):
        """
        Finishes the reading, e.g., for closing files or databases.
        """
        if self._current_input is not None:
            super().finalize()
            self._current_input.close()
            self._current_input = None


class XTunerWriter(BatchPairWriter):
    """
    Writer for the XTuner JSON format.
    """

    def __init__(self, target: str = None,
                 att_instruction: str = None, att_input: str = None, att_output: str = None,
                 pretty_print: bool = False, ensure_ascii: bool = True,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param att_instruction: the attribute with the instruction data
        :type att_instruction: str
        :param att_input: the attribute with the input data
        :type att_input: str
        :param att_output: the attribute with the output data
        :type att_output: str
        :param pretty_print: whether to output the JSON in more human-readable format
        :type pretty_print: bool
        :param ensure_ascii: whether to ensure ASCII compatible output
        :type ensure_ascii: bool
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.target = target
        self.att_instruction = att_instruction
        self.att_input = att_input
        self.att_output = att_output
        self.pretty_print = pretty_print
        self.ensure_ascii = ensure_ascii
        self._current_output = None
        self._output = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "to-xtuner"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Writes single-turn conversations in XTuner JSON format (https://github.com/InternLM/xtuner/blob/v0.1.13/docs/en/user_guides/dataset_format.md#single-turn-dialogue-dataset-format)."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path of the XTuner file to write (directory when processing multiple files)", required=True)
        parser.add_argument("--att_instruction", metavar="ATT", type=str, default=None, help="The attribute for the instructions", required=False)
        parser.add_argument("--att_input", metavar="ATT", type=str, default=None, help="The attribute for the inputs", required=False)
        parser.add_argument("--att_output", metavar="ATT", type=str, default=None, help="The attribute for the outputs", required=False)
        parser.add_argument("-p", "--pretty_print", action="store_true", help="Whether to output the JSON in more human-readable format.", required=False)
        parser.add_argument("-a", "--ensure_ascii", action="store_true", help="Whether to ensure that the output is ASCII compatible.", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.target = ns.output
        self.att_instruction = ns.att_instruction
        self.att_input = ns.att_input
        self.att_output = ns.att_output
        self.pretty_print = ns.pretty_print
        self.ensure_ascii = ns.ensure_ascii

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        if self.att_instruction is None:
            self.att_instruction = "system"
        if self.att_input is None:
            self.att_input = "input"
        if self.att_output is None:
            self.att_output = "output"

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PairData
        :type data: Iterable
        """
        if self._has_input_changed(update=True) and self._output_needs_changing(self._current_output, self.target, ".json"):
            self.finalize()
            self._current_output = generate_output(self.session.current_input, self.target, ".json", self.session.options.compression)
            self.logger().info("Writing to: " + self._current_output)
            self._output = open_file(self._current_output, mode="wt")

        dicts = []
        for item in data:
            _instruction = "" if (item.instruction is None) else item.instruction
            _input = "" if (item.input is None) else item.input
            _output = "" if (item.output is None) else item.output
            d = {
                self.att_instruction: _instruction,
                self.att_input: _input,
                self.att_output: _output
            }
            dicts.append(d)
        indent = 2 if self.pretty_print else None
        json.dump(dicts, self._output, ensure_ascii=self.ensure_ascii, indent=indent)

    def finalize(self):
        """
        Finishes the writing, e.g., for closing files or databases.
        """
        if self._output is not None:
            super().finalize()
            self._output.close()
            self._output = None
