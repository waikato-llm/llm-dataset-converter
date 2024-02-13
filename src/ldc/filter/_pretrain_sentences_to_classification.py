import argparse
from typing import List

from wai.logging import LOGGING_WARNING
from ldc.core import DOMAIN_CLASSIFICATION, DOMAIN_PRETRAIN, DEFAULT_END_CHARS
from ldc.pretrain import PretrainData
from ldc.supervised.classification import ClassificationData
from ldc.text_utils import split_into_sentences
from ._core import Filter


class PretrainSentencesToClassification(Filter):
    """
    Converts sentences from pretrain records to text classification ones by using X sentences
    as the text and the specified label.
    Can be used to generate classification datasets from just pretrain data.
    """

    def __init__(self, end_chars: str = DEFAULT_END_CHARS, num_sentences_text: int = 5, label: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param end_chars: the characters that signify the ending of a sentence
        :type end_chars: str
        :param num_sentences_text: the number of sentences following the prompt to use as response
        :type num_sentences_text: int
        :param label: the label to use
        :type label: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.end_chars = end_chars
        self.num_sentences_text = num_sentences_text
        self.label = label

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "pretrain-sentences-to-classification"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Converts sentences from pretrain records to text classification ones by using X sentences as text and the specified label. " \
               + "Can be used to generate classification datasets from just pretrain data."

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_CLASSIFICATION, DOMAIN_PRETRAIN]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PretrainData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [ClassificationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-c", "--end_chars", type=str, help="The characters signifying the end of a sentence.", default=DEFAULT_END_CHARS, required=False)
        parser.add_argument("-r", "--num_sentences_text", type=int, help="The number of sentences following the prompt sentence to use as response.", default=5, required=False)
        parser.add_argument("-L", "--label", type=str, help="The label to use.", default=None, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.end_chars = ns.end_chars
        self.num_sentences_text = ns.num_sentences_text
        self.label = ns.label

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.end_chars is None:
            self.end_chars = ""
        if len(self.end_chars) == 0:
            raise Exception("At least one character required to identify the end of a sentence!")
        if (self.label is None) or (len(self.label) == 0):
            raise Exception("No label provided!")
        if self.num_sentences_text < 1:
            raise Exception("Number of sentences making up a response must be at least 1, provided: %d" % self.num_sentences_text)

    def _do_process(self, data: PretrainData):
        """
        Processes the data record.

        :param data: the record to process
        :type data: ClassificationData
        :return: the potentially updated record(s)
        """
        result = []

        lines = data.content.split("\n")
        sentences = split_into_sentences(lines, self.end_chars)

        i = 0
        while True:
            if i + self.num_sentences_text < len(sentences):
                text = " ".join(sentences[i:i+self.num_sentences_text])
                result.append(ClassificationData(text=text, label=self.label))
            else:
                break
            i += self.num_sentences_text

        self.logger().info("# lines -> # classification records: %d -> %d" % (len(lines), len(result)))

        if len(result) == 1:
            result = result[0]
        return result
