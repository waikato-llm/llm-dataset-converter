import argparse
import jsonlines
from typing import Iterable, List, Union

from ldc.core import LOGGING_WARN, domain_suffix
from ldc.io import locate_files, open_file, generate_output
from ._core import TranslationData, TranslationReader, BatchTranslationWriter

DATA_EXAMPLE = '{ "translation": { "en": "Others have dismissed him as a joke.", "ro": "Alții l-au numit o glumă." } }'
DATA_DEFINITION_URL = "https://github.com/huggingface/transformers/blob/main/examples/pytorch/translation/README.md"


class JsonLinesTranslationReader(TranslationReader):
    """
    Reader for the JsonLines JSON format.
    """

    def __init__(self, source: Union[str, List[str]] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.source = source
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
        parser.add_argument("-i", "--input", type=str, help="Path to the JsonLines file(s) to read; glob syntax is supported", required=True, nargs="+")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.source = ns.input

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, fail_if_empty=True)

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
        self._current_input = open_file(self._current_input, mode="rt")

        self._reader = jsonlines.Reader(self._current_input)
        for item in self._reader:
            if "translation" in item:
                translations = item["translation"]

                yield TranslationData(
                    translations=translations,
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


class JsonLinesTranslationWriter(BatchTranslationWriter):
    """
    Writer for the JsonLines JSON format.
    """

    def __init__(self, target: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.target = target
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
        return "Writes prompt/output pairs in JsonLines-like JSON format. Example: %s" % DATA_EXAMPLE

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path of the JsonLines file to write (directory when processing multiple files)", required=True)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.target = ns.output

    def write_batch(self, data: Iterable[TranslationData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of TranslationData
        :type data: Iterable
        """
        if self._has_input_changed(update=True):
            self.finalize()
            output = generate_output(self.session.current_input, self.target, ".json", self.session.options.compression)
            self.logger().info("Writing to: " + output)
            self._output = open_file(output, mode="wt")

        self._writer = jsonlines.Writer(self._output)
        for item in data:
            d = {"translation": item.translations}
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
