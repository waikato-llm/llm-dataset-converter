import argparse

from ldc.core import LOGGING_WARN, DEFAULT_END_CHARS, DEFAULT_QUOTE_CHARS
from ._core import PretrainData, PretrainFilter, assemble_preformatted, split_into_sentences


class PretrainSentences(PretrainFilter):
    """
    Keeps or discards data records based on keyword(s).
    """

    def __init__(self, end_chars: str = DEFAULT_END_CHARS, quote_chars: str = DEFAULT_QUOTE_CHARS,
                 logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param end_chars: the characters that signify the ending of a sentence
        :type end_chars: str
        :param quote_chars: the characters that represent quotes
        :type quote_chars: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.end_chars = end_chars
        self.quote_chars = quote_chars

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "pretrain-sentences"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Splits pretrain text data into sentences and puts them on separate lines (using new-lines)."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-c", "--end_chars", type=str, help="The characters signifying the end of a sentence.", default=DEFAULT_END_CHARS, required=False)
        parser.add_argument("-q", "--quote_chars", type=str, help="The characters that represent quotes.", default=DEFAULT_QUOTE_CHARS, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.end_chars = ns.end_chars
        self.quote_chars = ns.quote_chars

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.end_chars is None:
            self.end_chars = ""
        if self.quote_chars is None:
            self.quote_chars = ""

    def process(self, data: PretrainData):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data

        lines = data.content.split("\n")
        pre = len(lines)
        lines = assemble_preformatted(lines, end_chars=self.end_chars, quote_chars=self.quote_chars)
        lines = split_into_sentences(lines, end_chars=self.end_chars)
        post = len(lines)
        if post == pre:
            return result
        self.logger().info("splitting into sentences, #lines: %d -> %d" % (pre, post))

        return PretrainData(
            content="\n".join(lines),
            meta=data.meta
        )
