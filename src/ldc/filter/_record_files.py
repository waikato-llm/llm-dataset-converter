import argparse
from typing import List

from wai.logging import LOGGING_WARNING

from ldc.api import Filter, strip_filename
from ldc.api.pretrain import PretrainData
from ldc.api.supervised.pairs import PairData
from ldc.api.translation import TranslationData
from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION


class RecordFiles(Filter):
    """
    Records the file names in the meta-data ('file') and outputs them, either to a file or stdout.
    """

    def __init__(self, output_file: str = None,
                 ignore_path: bool = False, ignore_extension: bool = False,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param output_file: the file to write the recorded files to, stdout if None
        :type output_file: str
        :param ignore_path: whether to remove the directory path from the filenames
        :type ignore_path: bool
        :param ignore_extension: whether to strip the file extension from the filename
        :type ignore_extension: bool
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.output_file = output_file
        self.ignore_path = ignore_path
        self.ignore_extension = ignore_extension
        self._files = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "record-files"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Records the file names in the meta-data ('file') and outputs them, either to a file or stdout."

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output_file", type=str, default=None, help="The file to write the the recorded files to; prints them to stdout if not provided.", required=False)
        parser.add_argument("-p", "--ignore_path", action="store_true", help="Whether to ignore the path in files when checking against the file list")
        parser.add_argument("-e", "--ignore_extension", action="store_true", help="Whether to ignore the extension in files when checking against the file list")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.output_file = ns.output_file
        self.ignore_path = ns.ignore_path
        self.ignore_extension = ns.ignore_extension

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._files = set()

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        if data.has_metadata():
            meta = data.get_metadata()
            if "file" in meta:
                filename = strip_filename(meta["file"], strip_path=self.ignore_path, strip_extension=self.ignore_extension)
                self._files.add(filename)

        return data

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        files = sorted(list(self._files))
        if self.output_file is not None:
            with open(self.output_file, "w") as fp:
                for f in files:
                    fp.write(f)
                    fp.write("\n")
        else:
            for f in files:
                print(f)
