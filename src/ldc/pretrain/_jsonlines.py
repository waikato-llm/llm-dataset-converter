import argparse
import jsonlines
from typing import Iterable, List, Union

from ldc.core import LOGGING_WARN, domain_suffix
from ldc.io import locate_files, open_file, generate_output
from ._core import PretrainData, PretrainReader, BatchPretrainWriter
from ldc.utils import add_meta_data


class JsonLinesPretrainReader(PretrainReader):
    """
    Reader for the JsonLines JSON format.
    """

    def __init__(self, source: Union[str, List[str]] = None, att_content: str = None, att_id: str = None,
                 att_meta: List[str] = None, logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param att_content: the attribute with the content
        :type att_content: str
        :param att_id: the (optional) attribute the ID
        :type att_id: str
        :param att_meta: the attributes to store in the meta-data, can be None
        :type att_meta: list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.source = source
        self.att_content = att_content
        self.att_id = att_id
        self.att_meta = att_meta
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
        return "Reads pretrain data in JsonLines-like JSON format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the JsonLines file(s) to read; glob syntax is supported", required=True, nargs="+")
        parser.add_argument("--att_content", metavar="ATT", type=str, default=None, help="The attribute with the text content", required=False)
        parser.add_argument("--att_id", metavar="ATT", type=str, default=None, help="The attribute the record ID (gets stored under 'id' in meta-data)", required=False)
        parser.add_argument("--att_meta", metavar="ATT", type=str, default=None, help="The attributes to store in the meta-data", required=False, nargs="*")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.source = ns.input
        self.att_content = ns.att_content
        self.att_id = ns.att_id
        self.att_meta = ns.att_meta

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, fail_if_empty=True)
        if self.att_content is None:
            raise Exception("No content attribute specified!")

    def read(self) -> Iterable[PretrainData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: PretrainData
        """
        self.finalize()

        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_input = open_file(self._current_input, mode="rt")

        self._reader = jsonlines.Reader(self._current_input)
        for item in self._reader:
            val_content = None
            if self.att_content is not None:
                val_content = item[self.att_content]

            id_ = None
            if self.att_id is not None:
                id_ = item[self.att_id]

            meta = None

            # ID?
            if id_ is not None:
                meta = add_meta_data(meta, "id", id_)

            # additional meta-data columns
            if self.att_meta is not None:
                for c in self.att_meta:
                    if c in item:
                        meta = add_meta_data(meta, c, item[c])

            yield PretrainData(
                content=val_content,
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


class JsonLinesPretrainWriter(BatchPretrainWriter):
    """
    Writer for the JsonLines JSON format.
    """

    def __init__(self, target: str = None, att_content: str = None, att_id: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param att_content: the attribute with the content
        :type att_content: str
        :param att_id: the (optional) attribute with the ID
        :type att_id: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.target = target
        self.att_content = att_content
        self.att_id = att_id
        self._current_output = None
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
        return "Writes pretrain data in JsonLines-like JSON format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path of the JsonLines file to write (directory when processing multiple files)", required=True)
        parser.add_argument("--att_content", metavar="ATT", type=str, default=None, help="The attribute for the text content", required=False)
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
        self.att_content = ns.att_content
        self.att_id = ns.att_id

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.att_content is None:
            raise Exception("No content attribute specified!")

    def write_batch(self, data: Iterable[PretrainData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PretrainData
        :type data: Iterable
        """
        if self._has_input_changed(update=True) and self._output_needs_changing(self._current_output, self.target, ".jsonl"):
            self.finalize()
            self._current_output = generate_output(self.session.current_input, self.target, ".jsonl", self.session.options.compression)
            self.logger().info("Writing to: " + self._current_output)
            self._output = open_file(self._current_output, mode="wt")
            self._writer = jsonlines.Writer(self._output)

        for item in data:
            d = {self.att_content: item.content}
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
