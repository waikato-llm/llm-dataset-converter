import argparse
import jsonlines
from typing import Iterable, List, Union

from ldc.core import LOGGING_WARN
from ldc.io import locate_files, open_file, generate_output
from ._core import PairData, PairReader, BatchPairWriter


class JsonLinesReader(PairReader):
    """
    Reader for the JsonLines JSON format.
    """

    def __init__(self, source: Union[str, List[str]] = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.source = source
        self._inputs = None
        self._current_input = None
        self._reader = None
        self.att_instruction = "instruction"
        self.att_input = "input"
        self.att_output = "output"

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-jsonlines-pairs"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Reads prompt/output pairs in JsonLines-like JSON format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the JsonLines file(s) to read; global syntax is supported", required=True, nargs="+")
        parser.add_argument("--att_instruction", metavar="COL", type=str, default=None, help="The attribute with the instructions", required=False)
        parser.add_argument("--att_input", metavar="COL", type=str, default=None, help="The attribute with the inputs", required=False)
        parser.add_argument("--att_output", metavar="COL", type=str, default=None, help="The attribute with the outputs", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.source = ns.input
        self.att_instruction = ns.att_instruction
        self.att_input = ns.att_input
        self.att_output = ns.att_output

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, fail_if_empty=True)
        if (self.att_instruction is None) and (self.att_input is None) and (self.att_output is None):
            raise Exception("No attributes specified!")

    def read(self) -> Iterable[PairData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: PairData
        """
        self.finalize()

        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        if self.logging_level:
            self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_input = open_file(self._current_input, mode="rt")
        self.session.input_changed = True
        
        self._reader = jsonlines.Reader(self._current_input)
        for item in self._reader:
            val_instruction = None
            if self.att_instruction is not None:
                val_instruction = item[self.att_instruction]
            val_input = None
            if self.att_input is not None:
                val_input = item[self.att_input]
            val_output = None
            if self.att_output is not None:
                val_output = item[self.att_output]
            yield PairData(
                instruction=val_instruction,
                input=val_input,
                output=val_output,
            )

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
            self._reader.close()
            self._reader = None
            self._current_input.close()
            self._current_input = None


class JsonLinesWriter(BatchPairWriter):
    """
    Writer for the JsonLines JSON format.
    """

    def __init__(self, target: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.target = target
        self._output = None
        self._writer = None
        self.att_instruction = None
        self.att_input = None
        self.att_output = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "to-jsonlines-pairs"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Writes prompt/output pairs in JsonLines-like JSON format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path of the JsonLines file to write (directory when processing multiple files)", required=True)
        parser.add_argument("--att_instruction", metavar="COL", type=str, default=None, help="The attribute for the instructions", required=False)
        parser.add_argument("--att_input", metavar="COL", type=str, default=None, help="The attribute for the inputs", required=False)
        parser.add_argument("--att_output", metavar="COL", type=str, default=None, help="The attribute for the outputs", required=False)
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
        if (self.att_instruction is None) and (self.att_input is None) and (self.att_output is None):
            raise Exception("No attributes specified!")

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PairData
        :type data: Iterable
        """
        if self.session.input_changed:
            self.finalize()
            output = generate_output(self.session.current_input, self.target, ".json", self.session.options.compression)
            if self.logging_level:
                self.logger().info("Writing to: " + output)
            self._output = open_file(output, mode="wt")

        self._writer = jsonlines.Writer(self._output)
        for item in data:
            d = dict()
            if self.att_instruction is not None:
                d[self.att_instruction] = item.instruction
            if self.att_input is not None:
                d[self.att_input] = item.input
            if self.att_output is not None:
                d[self.att_output] = item.output
            self._writer.write(d)

    def finalize(self):
        """
        Finishes the writing, e.g., for closing files or databases.
        """
        if self._output is not None:
            super().finalize()
            self._writer.close()
            self._writer = None
            self._output.close()
            self._output = None
