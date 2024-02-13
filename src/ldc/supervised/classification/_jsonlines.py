import argparse
import jsonlines
import os
from typing import Iterable, List, Union

from wai.logging import LOGGING_WARNING
from seppl import add_metadata
from seppl.io import locate_files
from ldc.core import domain_suffix
from ldc.base_io import open_file, generate_output, is_compressed
from ._core import ClassificationData, ClassificationReader, StreamClassificationWriter


class JsonLinesClassificationReader(ClassificationReader):
    """
    Reader for the JsonLines JSON format.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 att_text: str = None, att_label: str = None, att_id: str = None,
                 att_meta: List[str] = None, encoding: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param att_text: the attribute with the text
        :type att_text: str
        :param att_label: the attribute with the label
        :type att_label: str
        :param att_id: the (optional) attribute the ID
        :type att_id: str
        :param att_meta: the attributes to store in the meta-data, can be None
        :type att_meta: list
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
        self.att_text = att_text
        self.att_label = att_label
        self.att_id = att_id
        self.att_meta = att_meta
        self.encoding = encoding
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
        return "Reads classification data in JsonLines-like JSON format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the JsonLines file(s) to read; glob syntax is supported", required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the data files to use", required=False, nargs="*")
        parser.add_argument("--att_text", metavar="ATT", type=str, default=None, help="The attribute with the text data", required=False)
        parser.add_argument("--att_label", metavar="ATT", type=str, default=None, help="The attribute with the label", required=False)
        parser.add_argument("--att_id", metavar="ATT", type=str, default=None, help="The attribute the record ID (gets stored under 'id' in meta-data)", required=False)
        parser.add_argument("--att_meta", metavar="ATT", type=str, default=None, help="The attributes to store in the meta-data", required=False, nargs="*")
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
        self.att_text = ns.att_text
        self.att_label = ns.att_label
        self.att_id = ns.att_id
        self.att_meta = ns.att_meta
        self.encoding = ns.encoding

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True)
        if (self.att_text is None) and (self.att_label is None):
            raise Exception("No attributes specified!")

    def read(self) -> Iterable[ClassificationData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: ClassificationData
        """
        self.finalize()

        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_input = open_file(self._current_input, mode="rt", encoding=self.encoding, logger=self.logger())

        self._reader = jsonlines.Reader(self._current_input)
        for item in self._reader:
            val_text = None
            if self.att_text is not None:
                val_text = item[self.att_text]
            val_label = None
            if self.att_label is not None:
                val_label = item[self.att_label]

            id_ = None
            if self.att_id is not None:
                id_ = item[self.att_id]

            meta = None

            # ID?
            if id_ is not None:
                meta = add_metadata(meta, "id", id_)

            # additional meta-data columns
            if self.att_meta is not None:
                for c in self.att_meta:
                    if c in item:
                        meta = add_metadata(meta, c, item[c])

            yield ClassificationData(
                text=val_text,
                label=val_label,
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


class JsonLinesClassificationWriter(StreamClassificationWriter):
    """
    Writer for the JsonLines JSON format.
    """

    def __init__(self, target: str = None,
                 att_text: str = None, att_label: str = None, att_id: str = None,
                 num_digits: int = 6, buffer_size: int = 1000,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param att_text: the attribute with the text
        :type att_text: str
        :param att_label: the attribute with the label
        :type att_label: str
        :param att_id: the (optional) attribute with the ID
        :type att_id: str
        :param num_digits: the number of digits to use for the output file names
        :type num_digits: int
        :param buffer_size: the size of the record buffer (< 1 for unlimited)
        :type buffer_size: int
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.target = target
        self.att_text = att_text
        self.att_label = att_label
        self.att_id = att_id
        self.num_digits = num_digits
        self.buffer_size = buffer_size
        self._concatenate = False
        self._first_item = True
        self._fname_format = None
        self._buffer = []

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
        return "Writes classification data in JsonLines-like JSON format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path of the JsonLines file to write (directory when processing multiple files)", required=True)
        parser.add_argument("--att_text", metavar="ATT", type=str, default=None, help="The attribute for the text data", required=False)
        parser.add_argument("--att_label", metavar="ATT", type=str, default=None, help="The attribute for the label", required=False)
        parser.add_argument("--att_id", metavar="ATT", type=str, default=None, help="The name of the attribute for the row IDs (uses 'id' from meta-data)", required=False)
        parser.add_argument("-d", "--num_digits", metavar="NUM", type=int, default=6, help="The number of digits to use for the filenames", required=False)
        parser.add_argument("-b", "--buffer_size", metavar="SIZE", type=int, default=1000, help="The size of the record buffer when concatenating (to improve I/O throughput)", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.target = ns.output
        self.att_text = ns.att_text
        self.att_label = ns.att_label
        self.add_id = ns.att_id
        self.num_digits = ns.num_digits
        self.buffer_size = ns.buffer_size

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        if (self.att_text is None) and (self.att_label is None):
            raise Exception("No attributes specified!")
        self._first_item = True
        self._fname_format = "%0" + str(self.num_digits) + "d.txt"
        if os.path.exists(self.target) and os.path.isdir(self.target) and (not self.session.options.force_batch):
            self._concatenate = False
        else:
            self._concatenate = True
            if is_compressed(self.target):
                raise Exception("Cannot use compression when concatenating due to streaming!")
        self._buffer.clear()

    def _write(self, data: List[ClassificationData], output: str, mode: str):
        """
        Writes the data to disk.

        :param data: the records to write
        :type data: list
        :param output: the file to write to
        :type output: str
        :param mode: the file mode to use
        :type mode: str
        """
        with open(output, mode) as fp:
            writer = jsonlines.Writer(fp)
            for item in data:
                d = dict()
                if self.att_text is not None:
                    d[self.att_text] = item.text
                if self.att_label is not None:
                    d[self.att_label] = item.label
                if self.att_id is not None:
                    if (item.meta is not None) and ("id" in item.meta):
                        d[self.att_id] = item.meta["id"]
                try:
                    writer.write(d)
                except KeyboardInterrupt as e:
                    raise e
                except:
                    self.logger().exception("Failed to write record: %s" % str(d))
            writer.close()

    def _flush_buffer(self):
        """
        Writes the buffer content to disk.
        """
        self.logger().debug("flushing buffer: %d" % len(self._buffer))
        mode = "w" if self._first_item else "a"
        output_file = self.target
        if self.session.options.force_batch and os.path.isdir(output_file):
            output_file = generate_output(self.session.current_input, output_file, ".jsonl", None)
        if self._first_item:
            self.logger().info("Writing to: %s" % output_file)
        self._first_item = False
        self._write(self._buffer, output_file, mode)
        self._buffer.clear()

    def write_stream(self, data: Union[ClassificationData, Iterable[ClassificationData]]):
        """
        Saves the data one by one.

        :param data: the data to write
        :type data: PretrainData
        """
        if isinstance(data, ClassificationData):
            data = [data]

        if self._concatenate:
            self._buffer.extend(data)
            if len(self._buffer) >= self.buffer_size:
                self._flush_buffer()
        else:
            for item in data:
                if (item.meta is not None) and ("id" in item.meta):
                    try:
                        fname = self._fname_format % int(item.meta["id"])
                    except:
                        fname = str(item.meta["id"]) + ".jsonl"
                else:
                    fname = self._fname_format % self.session.count
                output = generate_output(fname, self.target, ".jsonl", self.session.options.compression)
                self.logger().info("Writing to: %s" % output)
                self._write([item], output, "w")

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        if len(self._buffer) > 0:
            self._flush_buffer()
