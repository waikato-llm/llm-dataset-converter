import argparse
import os
from typing import Iterable, List, Union

from ldc.core import LOGGING_WARN
from ldc.io import locate_files, open_file, generate_output, is_compressed
from ._core import PretrainData, PretrainReader, StreamPretrainWriter

METADATA_LINE = "line"


class TxtPretrainReader(PretrainReader):
    """
    Reader for plain text files.
    """

    def __init__(self, source: Union[str, List[str]] = None, split_lines: bool = False, logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param split_lines: whether to split the lines of the text into separate records
        :type split_lines: bool
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.source = source
        self.split_lines = split_lines
        self._inputs = None
        self._current_input = None
        self._reader = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-txt-pretrain"

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

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, fail_if_empty=True)

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
            self.session.input_changed = True
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
        return "to-txt-pretrain"

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
