import argparse
import jsonlines
from typing import Iterable, List, Union

from ldc.core import LOGGING_WARN, domain_suffix
from ldc.io import locate_files, open_file, generate_output
from ._core import PairData, PairReader, BatchPairWriter


class JsonLinesPairReader(PairReader):
    """
    Reader for the JsonLines JSON format.
    """

    def __init__(self, source: Union[str, List[str]] = None,
                 att_instruction: str = None, att_input: str = None, att_output: str = None, att_id: str = None,
                 logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param att_instruction: the attribute with the instruction data
        :type att_instruction: str
        :param att_input: the attribute with the input data
        :type att_input: str
        :param att_output: the attribute with the output data
        :type att_output: str
        :param att_id: the (optional) attribute the ID
        :type att_id: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.source = source
        self.att_instruction = att_instruction
        self.att_input = att_input
        self.att_output = att_output
        self.att_id = att_id
        self._inputs = None
        self._current_input = None
        self._reader = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-jsonlines-" + domain_suffix(self)

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
        parser.add_argument("-i", "--input", type=str, help="Path to the JsonLines file(s) to read; glob syntax is supported", required=True, nargs="+")
        parser.add_argument("--att_instruction", metavar="ATT", type=str, default=None, help="The attribute with the instructions", required=False)
        parser.add_argument("--att_input", metavar="ATT", type=str, default=None, help="The attribute with the inputs", required=False)
        parser.add_argument("--att_output", metavar="ATT", type=str, default=None, help="The attribute with the outputs", required=False)
        parser.add_argument("--att_id", metavar="ATT", type=str, default=None, help="The attribute the record ID (gets stored under 'id' in meta-data)", required=False)
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
        self.att_id = ns.att_id

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
        self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_input = open_file(self._current_input, mode="rt")

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

            id_ = None
            if self.att_id is not None:
                id_ = item[self.att_id]

            meta = None
            if id_ is not None:
                meta = {"id": id_}

            yield PairData(
                instruction=val_instruction,
                input=val_input,
                output=val_output,
                meta=meta,
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


class JsonLinesPairWriter(BatchPairWriter):
    """
    Writer for the JsonLines JSON format.
    """

    def __init__(self, target: str = None,
                 att_instruction: str = None, att_input: str = None, att_output: str = None, att_id: str = None,
                 logging_level: str = LOGGING_WARN):
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
        :param att_id: the (optional) attribute with the ID
        :type att_id: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.target = target
        self.att_instruction = att_instruction
        self.att_input = att_input
        self.att_output = att_output
        self.att_id = att_id
        self._output = None
        self._writer = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "to-jsonlines-" + domain_suffix(self)

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
        parser.add_argument("--att_instruction", metavar="ATT", type=str, default=None, help="The attribute for the instructions", required=False)
        parser.add_argument("--att_input", metavar="ATT", type=str, default=None, help="The attribute for the inputs", required=False)
        parser.add_argument("--att_output", metavar="ATT", type=str, default=None, help="The attribute for the outputs", required=False)
        parser.add_argument("--att_id", metavar="ATT", type=str, default=None, help="The name of the attribute for the row IDs (uses 'id' from meta-data)", required=False)
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
        self.add_id = ns.att_id

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        if (self.att_instruction is None) and (self.att_input is None) and (self.att_output is None):
            raise Exception("No attributes specified!")

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PairData
        :type data: Iterable
        """
        if self._has_input_changed(update=True):
            self.finalize()
            output = generate_output(self.session.current_input, self.target, ".json", self.session.options.compression)
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
            if self.att_id is not None:
                if (item.meta is not None) and ("id" in item.meta):
                    d[self.att_id] = item.meta["id"]
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
