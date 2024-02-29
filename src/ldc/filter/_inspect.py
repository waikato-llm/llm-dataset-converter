import argparse
import os
import sys
from typing import List, Union

from wai.logging import LOGGING_WARNING

from ldc.api import Filter
from ldc.core import DOMAIN_ANY
from seppl import get_metadata, AnyData, get_class_name
from ldc.api.supervised.pairs import PairData
from ldc.api.supervised.classification import ClassificationData
from ldc.api.pretrain import PretrainData
from ldc.api.translation import TranslationData
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATION_TEXT, LOCATIONS, locations_match, add_location_argument


MODE_INTERACTIVE = "interactive"
MODE_NONINTERACTIVE = "non-interactive"
MODES = [
    MODE_INTERACTIVE,
    MODE_NONINTERACTIVE,
]

OUTPUT_STDOUT = "stdout"
OUTPUT_STDERR = "stderr"
OUTPUT_LOGGER = "logger"
OUTPUT_FILE = "file"
OUTPUTS = [
    OUTPUT_STDOUT,
    OUTPUT_STDERR,
    OUTPUT_LOGGER,
    OUTPUT_FILE,
]


class Inspect(Filter):
    """
    Allows inspecting the data flowing through the pipeline.
    """

    def __init__(self, mode: str = MODE_INTERACTIVE, output: str = OUTPUT_STDOUT,
                 output_file: str = None, location: Union[str, List[str]] = LOCATION_ANY,
                 languages: List[str] = None, meta_data_keys: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param mode: the mode to operate in
        :type mode: str
        :param output: how to output the data
        :type output: str
        :param output_file: the file to store the data in (in case of OUTPUT_FILE)
        :type output_file: str
        :param location: what textual data to output
        :type location: str or list
        :param languages: the language(s) to output
        :type languages: list
        :param meta_data_keys: the keys of the meta-data value to output
        :type meta_data_keys: list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)

        if mode not in MODES:
            raise Exception("Unsupported mode: %s" % mode)
        if output not in OUTPUTS:
            raise Exception("Unsupported output: %s" % output)
        if location not in LOCATIONS:
            raise Exception("Invalid location: %s" % location)

        self.mode = mode
        self.output = output
        self.output_file = output_file
        self.location = location
        self.languages = languages
        self.meta_data_keys = meta_data_keys

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "inspect"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Allows inspecting the data flowing through the pipeline."

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_ANY]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [AnyData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [AnyData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-m", "--mode", choices=MODES, default=MODE_INTERACTIVE, help="The mode to operate in.")
        parser.add_argument("-o", "--output", choices=OUTPUTS, default=OUTPUT_STDOUT, help="How to output the data.")
        parser.add_argument("--output_file", type=str, default=None, help="The file to store the data in, in case of output '" + OUTPUT_FILE + "'.")
        add_location_argument(parser, "Which textual data to output", default=None)
        parser.add_argument("-g", "--language", type=str, help="The language(s) to output", required=False, nargs="*")
        parser.add_argument("-k", "--meta-data-key", metavar="KEY", type=str, help="The meta-data value to output", required=False, nargs="*")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.mode = ns.mode
        self.output = ns.output
        self.output_file = ns.output_file
        self.location = ns.location
        self.languages = ns.language
        self.meta_data_keys = ns.meta_data_key

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if (self.output == OUTPUT_FILE) and ((self.output_file is None) or (self.output_file == "")):
            raise Exception("No output file provided!")
        if (self.output == OUTPUT_FILE) and (os.path.exists(self.output_file)):
            if os.path.isdir(self.output_file):
                raise Exception("Output file points to directory: %s" % self.output_file)
            os.remove(self.output_file)

    def _assemble_data(self, data) -> str:
        """
        Assembles the requested data from the record.

        :param data: the record to get the data from
        :return: the generated string
        :rtype: str
        """
        result = []

        if isinstance(data, PairData):
            if locations_match(self.location, LOCATION_INSTRUCTION):
                result.append("%s: %s" % (LOCATION_INSTRUCTION, data.instruction))
            if locations_match(self.location, LOCATION_INPUT):
                result.append("%s: %s" % (LOCATION_INPUT, data.input))
            if locations_match(self.location, LOCATION_OUTPUT):
                result.append("%s: %s" % (LOCATION_OUTPUT, data.output))
        elif isinstance(data, ClassificationData):
            if locations_match(self.location, LOCATION_TEXT):
                result.append("%s: %s" % (LOCATION_TEXT, data.text))
        elif isinstance(data, PretrainData):
            if locations_match(self.location, LOCATION_CONTENT):
                result.append("%s: %s" % (LOCATION_CONTENT, data.content))
        elif isinstance(data, TranslationData):
            if self.languages is not None:
                for lang in self.languages:
                    if lang in data.translations:
                        result.append("lang[%s]: %s" % (lang, data.translations[lang]))
        else:
            self.logger().warning("Unhandled data type: %s" % get_class_name(data))

        if self.meta_data_keys is not None:
            meta = get_metadata(data)
            if meta is not None:
                for key in self.meta_data_keys:
                    if key in meta:
                        result.append("meta[%s]: %s" % (key, meta[key]))

        return "\n".join(result)

    def _output_data(self, data: str):
        """
        Outputs the requested data.
        """
        if self.output == OUTPUT_STDOUT:
            print(data)
        elif self.output == OUTPUT_STDERR:
            print(data, file=sys.stderr)
        elif self.output == OUTPUT_FILE:
            with open(self.output_file, "a") as fp:
                fp.write(data)
                fp.write("\n")
        else:
            raise Exception("Unsupported output: %s" % self.output)

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        self._output_data(self._assemble_data(data))

        if self.mode == MODE_INTERACTIVE:
            while True:
                print("Continue (yes/no/skip)? ")
                answer = input()
                answer = answer.lower()
                if (answer == "no") or (answer == "n"):
                    sys.exit(0)
                elif (answer == "skip") or (answer == "s"):
                    return None
                elif (answer == "yes") or (answer == "y"):
                    return data
                else:
                    print("Invalid choice!")
        else:
            return data
