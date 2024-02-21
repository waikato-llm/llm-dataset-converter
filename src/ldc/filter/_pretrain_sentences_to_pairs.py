import argparse
from typing import List

from seppl import add_metadata
from wai.logging import LOGGING_WARNING
from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN, DEFAULT_END_CHARS
from ldc.api.pretrain import PretrainData
from ldc.api.supervised.pairs import PairData
from ldc.text_utils import split_into_sentences
from ldc.api import Filter


class PretrainSentencesToPairs(Filter):
    """
    Converts sentences from pretrain records to prompt/response pairs by using one
    sentence as the prompt and the following X sentences as response.
    Can be used to generate artificial prompt/response datasets from just pretrain data.
    """

    def __init__(self, end_chars: str = DEFAULT_END_CHARS, prompt_step: int = 1, num_sentences_response: int = 5,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param end_chars: the characters that signify the ending of a sentence
        :type end_chars: str
        :param prompt_step: the step size for choosing sentences for prompts
        :type prompt_step: int
        :param num_sentences_response: the number of sentences following the prompt to use as response
        :type num_sentences_response: int
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.end_chars = end_chars
        self.prompt_step = prompt_step
        self.num_sentences_response = num_sentences_response

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "pretrain-sentences-to-pairs"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Converts sentences from pretrain records to prompt/response pairs by using one " \
               + "sentence as the prompt and the following X sentences as response. " \
               + "Can be used to generate artificial prompt/response datasets from just pretrain data."

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS, DOMAIN_PRETRAIN]

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
        return [PairData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-c", "--end_chars", type=str, help="The characters signifying the end of a sentence.", default=DEFAULT_END_CHARS, required=False)
        parser.add_argument("-p", "--prompt_step", type=int, help="The step size for selecting sentences as prompt; no sentence will be used for prompt if 0.", default=1, required=False)
        parser.add_argument("-r", "--num_sentences_response", type=int, help="The number of sentences following the prompt sentence to use as response.", default=5, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.end_chars = ns.end_chars
        self.prompt_step = ns.prompt_step
        self.num_sentences_response = ns.num_sentences_response

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.end_chars is None:
            self.end_chars = ""
        if len(self.end_chars) == 0:
            raise Exception("At least one character required to identify the end of a sentence!")
        if self.prompt_step < 0:
            raise Exception("Prompt step must be at least 0, provided: %d" % self.prompt_step)
        if self.num_sentences_response < 1:
            raise Exception("Number of sentences making up a response must be at least 1, provided: %d" % self.num_sentences_response)

    def _do_process(self, data: PretrainData):
        """
        Processes the data record.

        :param data: the record to process
        :type data: PairData
        :return: the potentially updated record(s)
        """
        result = []

        lines = data.content.split("\n")
        sentences = split_into_sentences(lines, self.end_chars)

        # metadata
        filename = None
        if data.has_metadata() and ("file" in data.get_metadata()):
            filename = data.get_metadata()["file"]

        i = 0
        while len(sentences) > 0:
            # prompt
            if self.prompt_step > 0:
                instruction = sentences.pop(0)
                i += 1
            else:
                instruction = ""

            # response
            response = []
            while (len(response) < self.num_sentences_response) and (len(sentences) > 0):
                response.append(sentences.pop(0))

            if len(response) > 0:
                meta = None
                if filename is not None:
                    meta = add_metadata(meta, "file", filename)
                output = " ".join(response)
                meta = add_metadata(meta, "output", str(i+self.prompt_step) + ":" + str(i+self.prompt_step+len(response) - 1))
                result.append(PairData(instruction=instruction, output=output, input=None, meta=meta))
                i += len(response)

        self.logger().info("#lines -> #sentences -> #records: %d -> %d -> %d" % (len(lines), len(sentences), len(result)))

        if len(result) == 1:
            result = result[0]
        return result
