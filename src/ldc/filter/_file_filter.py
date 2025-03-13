import argparse
import os.path
from typing import List

from wai.logging import LOGGING_WARNING

from ldc.api import Filter, FILTER_ACTIONS, FILTER_ACTION_DISCARD, FILTER_ACTION_KEEP, strip_filename
from ldc.api.pretrain import PretrainData
from ldc.api.supervised.pairs import PairData
from ldc.api.translation import TranslationData
from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION
from seppl.placeholders import PlaceholderSupporter, placeholder_list, expand_placeholders


class FileFilter(Filter, PlaceholderSupporter):
    """
    Keeps or discards records based on allow/discard lists for files matched against the 'file' meta-data value.
    """

    def __init__(self, file_list: str = None, action: str = FILTER_ACTION_KEEP,
                 missing_metadata_action: str = FILTER_ACTION_KEEP,
                 ignore_path: bool = False, ignore_extension: bool = False,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param file_list: the text file listing the to keep/to discard files
        :type file_list: str
        :param action: whether the listed files are to be kept or discarded
        :type action: str
        :param missing_metadata_action: what to do when there is no meta-data available
        :type missing_metadata_action: str
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

        if action not in FILTER_ACTIONS:
            raise Exception("Invalid action: %s" % action)

        self.file_list = file_list
        self.action = action
        self.missing_metadata_action = missing_metadata_action
        self.ignore_path = ignore_path
        self.ignore_extension = ignore_extension
        self._files = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "file-filter"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Keeps or discards records based on allow/discard lists for files matched against the 'file' meta-data value."

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
        parser.add_argument("-f", "--file_list", type=str, default=None, help="The file containing the files to be kept or discarded; " + placeholder_list(obj=self), required=True)
        parser.add_argument("-a", "--action", choices=FILTER_ACTIONS, default=FILTER_ACTION_KEEP, help="How to react when a record's 'file' meta-data value matches a filename from the list.")
        parser.add_argument("-m", "--missing_metadata_action", choices=FILTER_ACTIONS, default=FILTER_ACTION_KEEP, help="How to react when a record does not have the 'file' meta-data value.")
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
        self.file_list = ns.file_list
        self.action = ns.action
        self.missing_metadata_action = ns.missing_metadata_action
        self.ignore_path = ns.ignore_path
        self.ignore_extension = ns.ignore_extension

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._files = set()
        file_list = expand_placeholders(self.file_list)
        if not os.path.exists(file_list):
            raise Exception("File list does not exist: %s" % file_list)
        with open(file_list, "r") as fp:
            lines = [x.strip() for x in fp.readlines()]
        for line in lines:
            self._files.add(strip_filename(line, strip_path=self.ignore_path, strip_extension=self.ignore_extension))

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        if (not data.has_metadata()) and (self.missing_metadata_action == FILTER_ACTION_DISCARD):
            self.logger().debug("no meta-data at all, discarding")
            return None

        meta = data.get_metadata()
        if ("file" not in meta) and (self.missing_metadata_action == FILTER_ACTION_DISCARD):
            self.logger().debug("'file' not in meta-data, discarding")
            return None

        filename = strip_filename(meta["file"], strip_path=self.ignore_path, strip_extension=self.ignore_extension)

        result = data
        if self.action == FILTER_ACTION_DISCARD:
            if filename in self._files:
                result = None
        elif self.action == FILTER_ACTION_KEEP:
            if filename not in self._files:
                result = None
        else:
            raise Exception("Unhandled action: %s" % self.action)

        if result is None:
            self.logger().debug("discarding record with filename: %s" % filename)
        else:
            self.logger().debug("keeping record with filename: %s" % filename)

        return result
