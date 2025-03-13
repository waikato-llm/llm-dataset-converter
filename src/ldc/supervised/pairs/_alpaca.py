import argparse
import json
from typing import Iterable, List, Union

from wai.logging import LOGGING_WARNING
from seppl import add_metadata
from seppl.io import locate_files
from seppl.placeholders import PlaceholderSupporter, placeholder_list, expand_placeholders
from ldc.api import open_file, generate_output
from ldc.api.supervised.pairs import PairData, PairReader, BatchPairWriter


class AlpacaReader(PairReader, PlaceholderSupporter):
    """
    Reader for the Alpaca JSON format.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 encoding: str = None, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
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
        self.encoding = encoding
        self._inputs = None
        self._current_input = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-alpaca"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Reads prompt/output pairs in Alpaca-like JSON format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the Alpaca file(s) to read; glob syntax is supported; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the Alpaca files to use; " + placeholder_list(obj=self), required=False, nargs="*")
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
        self.encoding = ns.encoding

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True, default_glob="*.json")

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
            data = PairData.parse(item)
            meta = add_metadata(None, "file", self.session.current_input)
            data.set_metadata(meta)
            yield data

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


class AlpacaWriter(BatchPairWriter, PlaceholderSupporter):
    """
    Writer for the Alpaca JSON format.
    """

    def __init__(self, target: str = None, pretty_print: bool = False, ensure_ascii: bool = True, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
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
        return "to-alpaca"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Writes prompt/output pairs in Alpaca-like JSON format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path of the Alpaca file to write (directory when processing multiple files); " + placeholder_list(obj=self), required=True)
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
        self.pretty_print = ns.pretty_print
        self.ensure_ascii = ns.ensure_ascii

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

        dicts = [x.to_dict() for x in data]
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
