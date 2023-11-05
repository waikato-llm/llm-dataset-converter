import argparse
import os
import traceback
from typing import Iterable, List, Union

from ldc.core import LOGGING_WARN, domain_suffix, DEFAULT_END_CHARS, DEFAULT_QUOTE_CHARS
from ldc.base_io import locate_files, open_file, generate_output, is_compressed
from ._core import PretrainData, PretrainReader, StreamPretrainWriter
from ldc.text_utils import assemble_preformatted, split_into_sentences, combine_sentences, remove_empty, \
    remove_patterns, remove_blocks

METADATA_LINE = "line"


class TxtPretrainReader(PretrainReader):
    """
    Reader for plain text files.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 split_lines: bool = False, skip_empty: bool = False,
                 expr_remove: List[str] = None, sentences: bool = False, end_chars: str = DEFAULT_END_CHARS,
                 quote_chars: str = DEFAULT_QUOTE_CHARS,
                 block_removal_start: List[str] = None, block_removal_end: List[str] = None,
                 max_sentences: int = 1, logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param split_lines: whether to split the lines of the text into separate records
        :type split_lines: bool
        :param skip_empty: skips empty lines
        :type skip_empty: bool
        :param expr_remove: the list of regexp for removing sub-strings from the text
        :type expr_remove: list
        :param sentences: whether to assemble lines into sentences (eg when reading preformatted text)
        :type sentences: bool
        :param end_chars: the characters that signify the ending of a sentence
        :type end_chars: str
        :param quote_chars: the characters that represent quotes
        :type quote_chars: str
        :param block_removal_start: the start of blocks to remove
        :type block_removal_start: list
        :param block_removal_end: the end of blocks to remove
        :type block_removal_end: list
        :param max_sentences: the maximum number of sentences per line
        :type max_sentences: int
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.source = source
        self.source_list = source_list
        self.split_lines = split_lines
        self.skip_empty = skip_empty
        self.expr_remove = expr_remove
        self.sentences = sentences
        self.end_chars = end_chars
        self.quote_chars = quote_chars
        self.block_removal_start = block_removal_start
        self.block_removal_end = block_removal_end
        self.max_sentences = max_sentences
        self._inputs = None
        self._current_input = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-txt-" + domain_suffix(self)

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Reads pretrain data from plain text files, with each file representing a data record.\n" \
               + "Text files can be split into lines and forwarded as separate records as well."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the text file(s) to read; glob syntax is supported", required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the data files to use", required=False, nargs="*")
        parser.add_argument("-s", "--split_lines", action="store_true", help="Splits the text file on new lines and forwards them as separate records; the index of the line gets stored in the meta-data under '" + METADATA_LINE + "'.")
        parser.add_argument("-r", "--expr_remove", type=str, default=None, help="Regular expressions for removing sub-strings from the text (gets applied before skipping empty lines); uses re.sub(...).", nargs="*")
        parser.add_argument("-e", "--skip_empty", action="store_true", help="Removes empty lines from the data.")
        parser.add_argument("--sentences", action="store_true", help="For keeping sentences together, e.g., when reading preformatted text.")
        parser.add_argument("-c", "--end_chars", type=str, help="The characters signifying the end of a sentence.", default=DEFAULT_END_CHARS, required=False)
        parser.add_argument("-q", "--quote_chars", type=str, help="The characters that represent quotes.", default=DEFAULT_QUOTE_CHARS, required=False)
        parser.add_argument("--block_removal_start", type=str, help="The starting strings for blocks to remove", required=False, nargs="*")
        parser.add_argument("--block_removal_end", type=str, help="The ending strings for blocks to remove", required=False, nargs="*")
        parser.add_argument("-m", "--max_sentences", type=int, help="The maximum number of sentences per line.", default=1, required=False)
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
        self.split_lines = ns.split_lines
        self.skip_empty = ns.skip_empty
        self.expr_remove = ns.expr_remove
        self.sentences = ns.sentences
        self.end_chars = ns.end_chars
        self.quote_chars = ns.quote_chars
        self.block_removal_start = ns.block_removal_start
        self.block_removal_end = ns.block_removal_end
        self.max_sentences = ns.max_sentences

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True)
        if self.end_chars is None:
            self.end_chars = ""
        if self.quote_chars is None:
            self.quote_chars = ""
        if (self.block_removal_start is not None) and (self.block_removal_end is None):
            raise Exception("Block removal starts defined but no ends!")
        if (self.block_removal_start is None) and (self.block_removal_end is not None):
            raise Exception("Block removal ends defined but no starts!")
        if (self.block_removal_start is not None) and (self.block_removal_end is not None):
            if len(self.block_removal_start) != len(self.block_removal_end):
                raise Exception("Differing number of block removal starts and ends: %d != %d" % (len(self.block_removal_start), len(self.block_removal_end)))
        if self.max_sentences < 1:
            raise Exception("At least one sentence per line is required, currently set: %d" % self.max_sentences)

    def _remove_blocks(self, lines: List[str]) -> List[str]:
        """
        Removes blocks of text between the defined start/end strings (incl these strings).

        :param lines: the lines to process
        :type lines: list
        :return: the updated lines
        :rtype: list
        """
        pre = len(lines)
        result = remove_blocks(lines, self.block_removal_start, self.block_removal_end)
        post = len(result)
        self.logger().info("block removal, #lines: %d -> %d" % (pre, post))
        return result

    def _assemble_sentences(self, lines: List[str]) -> List[str]:
        """
        Assembles lines into sentences, e.g., when processing preformatted text.

        :param lines: the lines to process
        :type lines: list
        :return: the updated lines
        :rtype: list
        """
        pre = len(lines)
        result = assemble_preformatted(lines, end_chars=self.end_chars, quote_chars=self.quote_chars)
        result = split_into_sentences(result, end_chars=self.end_chars)
        result = combine_sentences(result, max_sentences=self.max_sentences)
        post = len(result)
        self.logger().info("assembling sentences, #lines: %d -> %d" % (pre, post))
        return result

    def _remove_patterns(self, lines: List[str]) -> List[str]:
        """
        Removes all lines that match the patterns (inline).

        :param lines: the lines to process
        :type lines: list
        :return: the processed lines
        :rtype: list
        """
        result, affected = remove_patterns(lines, self.expr_remove)
        self.logger().info("remove patterns, affected #lines: %d" % affected)
        return result

    def _remove_empty(self, lines: List[str]) -> List[str]:
        """
        Removes empty lines from the list and returns an updated list.

        :param lines: the lines to process
        :type lines: list
        :return: the updated list
        :rtype: list
        """
        pre = len(lines)
        result = remove_empty(lines)
        post = len(lines)
        self.logger().info("removing empty, #lines: %d -> %d" % (pre, post))
        return result

    def read(self) -> Iterable[PretrainData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: PretrainData
        """
        self.finalize()

        for input_file in self._inputs:
            self.session.current_input = input_file
            self.logger().info("Reading from: " + str(input_file))
            try:
                with open_file(self.session.current_input, mode="rt") as fp:
                    lines = fp.readlines()
            except KeyboardInterrupt as e:
                raise e
            except:
                self.logger().warning("Failed to read: %s\n%s" % (self.session.current_input, traceback.format_exc(1)))
                continue

            # remove blocks?
            if self.block_removal_start is not None:
                lines = self._remove_blocks(lines)
            # assemble sentences?
            if self.sentences:
                lines = self._assemble_sentences(lines)
            # remove patterns?
            if self.expr_remove is not None:
                lines = self._remove_patterns(lines)
            # skip empty?
            if self.skip_empty:
                lines = self._remove_empty(lines)

            if self.split_lines:
                for index, line in enumerate(lines):
                    yield PretrainData(
                        content=line.strip(),
                        meta={METADATA_LINE: index}
                    )
            else:
                yield PretrainData(
                    content="".join(lines)
                )
        self._inputs = []

    def has_finished(self) -> bool:
        """
        Returns whether reading has finished.

        :return: True if finished
        :rtype: bool
        """
        return len(self._inputs) == 0


class TxtPretrainWriter(StreamPretrainWriter):
    """
    Writer for the plain text files.
    """

    def __init__(self, target: str = None, num_digits: int = 6, buffer_size: int = 1000,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
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
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.target = target
        self.num_digits = num_digits
        self.buffer_size = buffer_size
        self._current_output = None
        self._output = None
        self._writer = None
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
        return "to-txt-" + domain_suffix(self)

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Writes pretrain data to plain text files.\n" \
               + "When providing an output directory, either uses the current session counter as the filename or, " \
               + "if present, the 'id' value from the meta-data.\n" \
               + "When providing an output file, all incoming content will be concatenated in this one file. " \
               + "Compression is not available in this case due to the streaming context."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path to the directory or file to write to", required=True)
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
        if os.path.exists(self.target) and os.path.isdir(self.target):
            self._concatenate = False
        else:
            self._concatenate = True
            if is_compressed(self.target):
                raise Exception("Cannot use compression when concatenating due to streaming!")
        self._buffer.clear()

    def _flush_buffer(self):
        """
        Writes the buffer content to disk.
        """
        self.logger().debug("flushing buffer: %d" % len(self._buffer))
        mode = "w" if self._first_item else "a"
        if self._first_item:
            self.logger().info("Writing to: %s" % self.target)
        self._first_item = False
        with open(self.target, mode) as fp:
            for d in self._buffer:
                try:
                    fp.write(d.content)
                    fp.write("\n")
                except KeyboardInterrupt as e:
                    raise e
                except:
                    self.logger().exception("Failed to write record: %s" % str(d))
        self._buffer.clear()

    def write_stream(self, data: Union[PretrainData, Iterable[PretrainData]]):
        """
        Saves the data one by one.

        :param data: the data to write
        :type data: PretrainData
        """
        if isinstance(data, PretrainData):
            data = [data]

        if self._concatenate:
            self._buffer.extend(data)
            if len(self._buffer) >= self.buffer_size:
                self._flush_buffer()
        else:
            for d in data:
                if (d.meta is not None) and ("id" in d.meta):
                    try:
                        fname = self._fname_format % int(d.meta["id"])
                    except:
                        fname = str(d.meta["id"]) + ".txt"
                else:
                    fname = self._fname_format % self.session.count
                output = generate_output(fname, self.target, ".txt", self.session.options.compression)
                self.logger().info("Writing to: %s" % output)
                with open(output, "w") as fp:
                    fp.write(d.content)

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        if len(self._buffer) > 0:
            self._flush_buffer()
