import argparse
import os
import re
from typing import Iterable, List, Union

from ldc.core import LOGGING_WARN, domain_suffix
from ldc.io import locate_files, open_file, generate_output, is_compressed
from ._core import PretrainData, PretrainReader, StreamPretrainWriter

METADATA_LINE = "line"

DEFAULT_END_CHARS = ".!?;:)"

DEFAULT_QUOTES = "\"'”’"


class TxtPretrainReader(PretrainReader):
    """
    Reader for plain text files.
    """

    def __init__(self, source: Union[str, List[str]] = None, split_lines: bool = False, skip_empty: bool = False,
                 expr_remove: List[str] = None, sentences: bool = False, end_chars: str = DEFAULT_END_CHARS,
                 block_removal_start: List[str] = None, block_removal_end: List[str] = None,
                 logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
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
        :param block_removal_start: the start of blocks to remove
        :type block_removal_start: list
        :param block_removal_end: the end of blocks to remove
        :type block_removal_end: list
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.source = source
        self.split_lines = split_lines
        self.skip_empty = skip_empty
        self.expr_remove = expr_remove
        self.sentences = sentences
        self.end_chars = end_chars
        self.block_removal_start = block_removal_start
        self.block_removal_end = block_removal_end
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
        parser.add_argument("-i", "--input", type=str, help="Path to the text file(s) to read; glob syntax is supported", required=True, nargs="+")
        parser.add_argument("-s", "--split_lines", action="store_true", help="Splits the text file on new lines and forwards them as separate records; the index of the line gets stored in the meta-data under '" + METADATA_LINE + "'.")
        parser.add_argument("-r", "--expr_remove", type=str, default=None, help="Regular expressions for removing sub-strings from the text (gets applied before skipping empty lines).", nargs="*")
        parser.add_argument("-e", "--skip_empty", action="store_true", help="Removes empty lines from the data.")
        parser.add_argument("--sentences", action="store_true", help="For keeping sentences together, e.g., when reading preformatted text.")
        parser.add_argument("-c", "--end_chars", type=str, help="The characters signifying the end of a sentence.", default=DEFAULT_END_CHARS, required=False)
        parser.add_argument("--block_removal_start", type=str, help="The starting strings for blocks to remove", required=False, nargs="*")
        parser.add_argument("--block_removal_end", type=str, help="The ending strings for blocks to remove", required=False, nargs="*")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.source = ns.input
        self.split_lines = ns.split_lines
        self.skip_empty = ns.skip_empty
        self.expr_remove = ns.expr_remove
        self.sentences = ns.sentences
        self.end_chars = ns.end_chars
        self.block_removal_start = ns.block_removal_start
        self.block_removal_end = ns.block_removal_end

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, fail_if_empty=True)
        if (self.block_removal_start is not None) and (self.block_removal_end is None):
            raise Exception("Block removal starts defined but no ends!")
        if (self.block_removal_start is None) and (self.block_removal_end is not None):
            raise Exception("Block removal ends defined but no starts!")
        if (self.block_removal_start is not None) and (self.block_removal_end is not None):
            if len(self.block_removal_start) != len(self.block_removal_end):
                raise Exception("Differing number of block removal starts and ends: %d != %d" % (len(self.block_removal_start), len(self.block_removal_end)))

    def _remove_blocks(self, lines: List[str]) -> List[str]:
        """
        Removes blocks of text between the defined start/end strings (incl these strings).

        :param lines: the lines to process
        :type lines: list
        :return: the updated lines
        :rtype: list
        """
        pre = len(lines)
        result = []
        in_block = False

        for line in lines:
            if in_block:
                for end in self.block_removal_end:
                    if end in line:
                        in_block = False
                        continue
            else:
                for start in self.block_removal_start:
                    if start in line:
                        in_block = True
                        break
                if not in_block:
                    result.append(line)

        post = len(result)
        self.logger().info("block removal, #lines: %d -> %d" % (pre, post))
        return result

    def _assemble_preformatted(self, lines: List[str]) -> List[str]:
        """
        Assembles preformatted lines into full sentences.

        :param lines: the lines to process
        :type lines: list
        :return: the updated lines
        :rtype: list
        """
        result = []
        new_sentence = False
        buffer = None

        for line in lines:
            line = line.strip()
            curr = line

            # remove quotes at end
            # TODO quotes
            if curr.endswith('"') or curr.endswith("'"):
                curr = curr[:len(curr) - 1]

            # new sentence?
            if len(curr) == 0:
                new_sentence = True
            else:
                for chr in self.end_chars:
                    if curr.endswith(chr):
                        new_sentence = True
                        break

            if new_sentence:
                new_sentence = False
                if len(line) > 0:
                    if buffer is None:
                        buffer = line
                    else:
                        buffer += " " + line
                if buffer is not None:
                    result.append(buffer)
                    buffer = None
            else:
                if buffer is None:
                    buffer = line
                else:
                    buffer += " " + line

        if buffer is not None:
            result.append(buffer)

        return result

    def _split_into_sentences(self, lines: List[str]) -> List[str]:
        """
        Splits text into separate sentences.

        :param lines: the lines to process
        :type lines: list
        :return: the updated lines
        :rtype: list
        """
        result = []

        for line in lines:
            while len(line) > 0:
                pos = len(line)
                for chr in self.end_chars:
                    if chr in line:
                        pos = min(pos, line.index(chr))
                if pos < len(line):
                    result.append(line[0:pos + 1].strip())
                    line = line[pos + 1:].strip()
                    # dangling end char?
                    if len(line) == 1:
                        result[-1] += line
                        line = ""
                else:
                    result.append(line.strip())
                    line = ""

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
        result = self._assemble_preformatted(lines)
        result = self._split_into_sentences(result)
        post = len(result)
        self.logger().info("assembling sentences, #lines: %d -> %d" % (pre, post))
        return result

    def _remove_patterns(self, lines: List[str]):
        """
        Removes all lines that match the patterns (inline).

        :param lines: the lines to process
        :type lines: list
        """
        affected = 0
        for i in range(len(lines)):
            for expr in self.expr_remove:
                new_line = re.sub(expr, "", lines[i])
                if len(lines[i]) != len(new_line):
                    lines[i] = new_line
                    affected += 1
        self.logger().info("remove patterns, affected #lines: %d" % affected)

    def _remove_empty(self, lines: List[str]) -> List[str]:
        """
        Removes empty lines from the list and returns an updated list.

        :param lines: the lines to process
        :type lines: list
        :return: the updated list
        :rtype: list
        """
        pre = len(lines)
        result = []
        for line in lines:
            if len(line.strip()) > 0:
                result.append(line)
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
            with open_file(self.session.current_input, mode="rt") as fp:
                lines = fp.readlines()

            # remove blocks?
            if self.block_removal_start is not None:
                lines = self._remove_blocks(lines)
            # assemble sentences?
            if self.sentences:
                lines = self._assemble_sentences(lines)
            # remove patterns?
            if self.expr_remove is not None:
                self._remove_patterns(lines)
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

    def __init__(self, target: str = None, num_digits: int = 6, logging_level: str = LOGGING_WARN):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param num_digits: the number of digits to use for the output file names
        :type num_digits: int
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.target = target
        self.num_digits = num_digits
        self._output = None
        self._writer = None
        self._concatenate = False
        self._first_item = True
        self._fname_format = None

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

    def write_stream(self, data: PretrainData):
        """
        Saves the data one by one.

        :param data: the data to write
        :type data: PretrainData
        """
        if self._concatenate:
            mode = "w" if self._first_item else "a"
            self._first_item = False
            with open(self.target, mode) as fp:
                fp.write(data.content)
                fp.write("\n")
        else:
            if (data.meta is not None) and ("id" in data.meta):
                try:
                    fname = self._fname_format % int(data.meta["id"])
                except:
                    fname = str(data.meta["id"]) + ".txt"
            else:
                fname = self._fname_format % self.session.count
            output = generate_output(fname, self.target, ".txt", self.session.options.compression)
            with open(output, "w") as fp:
                fp.write(data.content)
