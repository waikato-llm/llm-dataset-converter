import argparse
import jsonlines
import os
from typing import Iterable, List, Union

from wai.logging import LOGGING_WARNING
from seppl import add_metadata
from seppl.io import locate_files
from seppl.placeholders import PlaceholderSupporter, placeholder_list, expand_placeholders
from ldc.core import domain_suffix
from ldc.api import open_file, generate_output, is_compressed
from ldc.api.translation import TranslationData, TranslationReader, StreamTranslationWriter
from ldc.text_utils import empty_str_if_none

DATA_EXAMPLE = '{ "translation": { "en": "Others have dismissed him as a joke.", "ro": "Alții l-au numit o glumă." } }'
DATA_DEFINITION_URL = "https://github.com/huggingface/transformers/blob/main/examples/pytorch/translation/README.md"


class JsonLinesTranslationReader(TranslationReader, PlaceholderSupporter):
    """
    Reader for the JsonLines JSON format.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 att_meta: List[str] = None, encoding: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
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
        return "Reads translation in JsonLines-like JSON format. Example: %s" % DATA_EXAMPLE

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the JsonLines file(s) to read; glob syntax is supported; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the JsonLines files to use; " + placeholder_list(obj=self), required=False, nargs="*")
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
        self.att_meta = ns.att_meta
        self.encoding = ns.encoding

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True, default_glob="*.jsonl")

    def read(self) -> Iterable[TranslationData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: TranslationData
        """
        self.finalize()

        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_input = open_file(self._current_input, mode="rt", encoding=self.encoding, logger=self.logger())

        self._reader = jsonlines.Reader(self._current_input)
        for item in self._reader:
            if "translation" in item:
                translations = item["translation"]

                meta = None

                # file
                meta = add_metadata(meta, "file", self.session.current_input)

                # additional meta-data columns
                if self.att_meta is not None:
                    for c in self.att_meta:
                        if c in item:
                            meta = add_metadata(meta, c, item[c])

                yield TranslationData(
                    translations=translations,
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


class JsonLinesTranslationWriter(StreamTranslationWriter, PlaceholderSupporter):
    """
    Writer for the JsonLines JSON format.
    """

    def __init__(self, target: str = None,
                 num_digits: int = 6, buffer_size: int = 1000,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
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
        return "Writes prompt/output pairs in JsonLines-like JSON format. Example: %s" % DATA_EXAMPLE

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path of the JsonLines file to write (directory when processing multiple files); " + placeholder_list(obj=self), required=True)
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
        self.num_digits = ns.num_digits
        self.buffer_size = ns.buffer_size

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._first_item = True
        self._fname_format = "%0" + str(self.num_digits) + "d.txt"
        target = expand_placeholders(self.target)
        if os.path.exists(target) and os.path.isdir(target) and (not self.session.options.force_batch):
            self._concatenate = False
        else:
            self._concatenate = True
            if is_compressed(target):
                raise Exception("Cannot use compression when concatenating due to streaming!")
        self._buffer.clear()

    def _write(self, data: List[TranslationData], output: str, mode: str):
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
                d = {"translation": empty_str_if_none(item.translations)}
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
        output_file = expand_placeholders(self.target)
        if self.session.options.force_batch and os.path.isdir(output_file):
            output_file = generate_output(self.session.current_input, output_file, ".jsonl", None)
        if self._first_item:
            self.logger().info("Writing to: %s" % output_file)
        self._first_item = False
        self._write(self._buffer, output_file, mode)
        self._buffer.clear()

    def write_stream(self, data: Union[TranslationData, Iterable[TranslationData]]):
        """
        Saves the data one by one.

        :param data: the data to write
        :type data: PretrainData
        """
        if isinstance(data, TranslationData):
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
                target = expand_placeholders(self.target)
                output = generate_output(fname, target, ".jsonl", self.session.options.compression)
                self.logger().info("Writing to: %s" % output)
                self._write([item], output, "w")

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        if len(self._buffer) > 0:
            self._flush_buffer()
