import argparse
import copy

from ldc.core import LOGGING_WARN, DEFAULT_END_CHARS, DEFAULT_QUOTE_CHARS, domain_suffix
from ._core import PretrainData, PretrainFilter
from ldc.text_utils import assemble_preformatted, split_into_sentences, combine_sentences


class Sentences(PretrainFilter):
    """
    Splits pretrain text data into sentences and puts them on separate lines (using new-lines).
    """

    def __init__(self, end_chars: str = DEFAULT_END_CHARS, quote_chars: str = DEFAULT_QUOTE_CHARS,
                 max_sentences: int = 1, split_records: bool = False,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param end_chars: the characters that signify the ending of a sentence
        :type end_chars: str
        :param quote_chars: the characters that represent quotes
        :type quote_chars: str
        :param max_sentences: the maximum number of sentences per line
        :type max_sentences: int
        :param split_records: whether to split the records
        :type split_records: bool
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.end_chars = end_chars
        self.quote_chars = quote_chars
        self.max_sentences = max_sentences
        self.split_records = split_records

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "sentences-" + domain_suffix(self)

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
        parser.add_argument("-m", "--max_sentences", type=int, help="The maximum number of sentences per line.", default=1, required=False)
        parser.add_argument("-s", "--split_records", action="store_true", help="Splits the lines into separate records (one line per record) after reassambling the lines instead of combining them back into single document.", required=False)
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
        self.max_sentences = ns.max_sentences
        self.split_records = ns.split_records

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.end_chars is None:
            self.end_chars = ""
        if self.quote_chars is None:
            self.quote_chars = ""
        if self.max_sentences < 1:
            raise Exception("At least one sentence per line is required, currently set: %d" % self.max_sentences)

    def _do_process(self, data: PretrainData):
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
        lines = combine_sentences(lines, max_sentences=self.max_sentences)
        post = len(lines)
        if post == pre:
            return result
        self.logger().info("splitting into sentences, #lines: %d -> %d" % (pre, post))

        if self.split_records:
            result = []
            for line in lines:
                result.append(PretrainData(
                    content=line,
                    meta=copy.deepcopy(data.meta)
                ))
        else:
            result = PretrainData(
                content="\n".join(lines),
                meta=data.meta
            )

        return result
