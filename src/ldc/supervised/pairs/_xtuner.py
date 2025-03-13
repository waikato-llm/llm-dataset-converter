import argparse
import json
from typing import Iterable, List, Union

from wai.logging import LOGGING_WARNING
from seppl import add_metadata
from seppl.io import locate_files
from seppl.placeholders import PlaceholderSupporter, placeholder_list, expand_placeholders
from ldc.api import open_file, generate_output
from ldc.api.supervised.pairs import PairData, PairReader, BatchPairWriter


class XTunerReader(PairReader, PlaceholderSupporter):
    """
    Reader for the XTuner JSON format.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 att_system: str = None, att_input: str = None, att_output: str = None,
                 encoding: str = None, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param att_system: the attribute with the instruction data
        :type att_system: str
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
        self.att_system = att_system
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
        parser.add_argument("-i", "--input", type=str, help="Path to the XTuner file(s) to read; glob syntax is supported; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the XTuner files to use; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("--att_system", metavar="ATT", type=str, default=None, help="The attribute with the system instructions", required=False)
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
        self.att_system = ns.att_system
        self.att_input = ns.att_input
        self.att_output = ns.att_output
        self.encoding = ns.encoding

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True, default_glob="*.json")
        if self.att_system is None:
            self.att_system = "system"
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
                if self.att_system in conversation:
                    _instruction = conversation[self.att_system]
                if self.att_input in conversation:
                    _input = conversation[self.att_input]
                if self.att_output in conversation:
                    _output = conversation[self.att_output]
                meta = add_metadata(None, "file", self.session.current_input)
                yield PairData(instruction=_instruction, input=_input, output=_output, meta=meta)

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


PH_NEWLINE = "{NEWLINE}"
PH_TAB = "{TAB}"
PH_SYSTEM_TEXT = "{SYSTEM_TEXT}"
PH_INSTRUCTION = "{INSTRUCTION}"
PH_INPUT = "{INPUT}"
PH_OUTPUT = "{OUTPUT}"
PLACEHOLDERS = [
    PH_NEWLINE,
    PH_TAB,
    PH_SYSTEM_TEXT,
    PH_INSTRUCTION,
    PH_INPUT,
    PH_OUTPUT,
]


class XTunerWriter(BatchPairWriter, PlaceholderSupporter):
    """
    Writer for the XTuner JSON format.
    """

    def __init__(self, target: str = None,
                 att_system: str = None, att_input: str = None, att_output: str = None, text_system: str = None,
                 format_system: str = None, format_input: str = None, format_output: str = None,
                 pretty_print: bool = False, ensure_ascii: bool = True,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param att_system: the attribute with the instruction data
        :type att_system: str
        :param att_input: the attribute with the input data
        :type att_input: str
        :param att_output: the attribute with the output data
        :type att_output: str
        :param text_system: the text to use for the system instruction
        :type text_system: str
        :param format_system: the format (using placeholders) to use for the system instructions
        :type format_system: str
        :param format_input: the format (using placeholders) to use for the input
        :type format_input: str
        :param format_output: the format (using placeholders) to use for the output
        :type format_output: str
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
        self.att_system = att_system
        self.att_input = att_input
        self.att_output = att_output
        self.text_system = text_system
        self.format_system = format_system
        self.format_input = format_input
        self.format_output = format_output
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
        parser.add_argument("-o", "--output", type=str, help="Path of the XTuner file to write (directory when processing multiple files); " + placeholder_list(obj=self), required=True)
        parser.add_argument("--att_system", metavar="ATT", type=str, default=None, help="The attribute for the system instructions", required=False)
        parser.add_argument("--att_input", metavar="ATT", type=str, default=None, help="The attribute for the inputs", required=False)
        parser.add_argument("--att_output", metavar="ATT", type=str, default=None, help="The attribute for the outputs", required=False)
        parser.add_argument("--text_system", metavar="TEXT", type=str, default=None, help="The text to use for the system instructions; supports following placeholders: " + PH_NEWLINE + "|" + PH_TAB, required=False)
        parser.add_argument("--format_system", metavar="FORMAT", type=str, default=None, help="The format to use for the system instructions, available placeholders: " + "|".join(PLACEHOLDERS), required=False)
        parser.add_argument("--format_input", metavar="FORMAT", type=str, default=None, help="The format to use for the input, available placeholders: " + "|".join(PLACEHOLDERS), required=False)
        parser.add_argument("--format_output", metavar="FORMAT", type=str, default=None, help="The format to use for the output, available placeholders: " + "|".join(PLACEHOLDERS), required=False)
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
        self.att_system = ns.att_system
        self.att_input = ns.att_input
        self.att_output = ns.att_output
        self.text_system = ns.text_system
        self.format_system = ns.format_system
        self.format_input = ns.format_input
        self.format_output = ns.format_output
        self.pretty_print = ns.pretty_print
        self.ensure_ascii = ns.ensure_ascii

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        if self.att_system is None:
            self.att_system = "system"
        if self.att_input is None:
            self.att_input = "input"
        if self.att_output is None:
            self.att_output = "output"
        if (self.format_system is None) and (self.format_input is None) and (self.format_output is None):
            raise Exception("No formats defined for system/input/output!")

    def _apply_format(self, item: PairData, fmt: str) -> str:
        """
        Applies the format and returns the generated string.

        :param item: the pair data to use for generating the output
        :type item: PairData
        :param fmt: the format string
        :type fmt: str
        :return: the generated string
        :rtype: str
        """
        if (fmt is None) or (len(fmt) == 0):
            return ""

        _text_system = "" if (self.text_system is None) else self.text_system
        _text_system = _text_system.replace(PH_NEWLINE, "\n").replace(PH_TAB, "\t")
        _instruction = "" if (item.instruction is None) else item.instruction
        _input = "" if (item.input is None) else item.input
        _output = "" if (item.output is None) else item.output

        result = fmt.replace(PH_NEWLINE, "\n").replace(PH_TAB, "\t")
        result = result.replace(PH_SYSTEM_TEXT, _text_system)
        result = result.replace(PH_INSTRUCTION, _instruction)
        result = result.replace(PH_INPUT, _input)
        result = result.replace(PH_OUTPUT, _output)

        return result

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PairData
        :type data: Iterable
        """
        target = expand_placeholders(self.target)
        if self._has_input_changed(update=True) and self._output_needs_changing(self._current_output, target, ".json"):
            self.finalize()
            self._current_output = generate_output(self.session.current_input, target, ".json", self.session.options.compression)
            self.logger().info("Writing to: " + self._current_output)
            self._output = open_file(self._current_output, mode="wt")

        dicts = []
        for item in data:
            _instruction = "" if (item.instruction is None) else item.instruction
            _input = "" if (item.input is None) else item.input
            _output = "" if (item.output is None) else item.output
            d = {
                self.att_system: self._apply_format(item, self.format_system),
                self.att_input: self._apply_format(item, self.format_input),
                self.att_output: self._apply_format(item, self.format_output),
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
