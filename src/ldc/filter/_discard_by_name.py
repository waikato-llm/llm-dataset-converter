import argparse
import os
import re
from typing import List

from seppl import MetaDataHandler
from wai.logging import LOGGING_WARNING

from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION, DOMAIN_CLASSIFICATION
from ldc.api import Filter
from ldc.api.pretrain import PretrainData
from ldc.api.supervised.classification import ClassificationData
from ldc.api.supervised.pairs import PairData
from ldc.api.translation import TranslationData


class DiscardByName(Filter):
    """
    Discards files based on list of image names and/or regular expressions that image names must match.
    """

    def __init__(self, names: List[str] = None, names_file: str = None,
                 regexps: List[str] = None, regexps_file: str = None,
                 remove_ext: bool = None, invert: bool = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param names: the list of image names to drop
        :type names: list
        :param names_file: the text file with the image names to drop (one per line)
        :type names_file: str
        :param regexps: the regular expressions for dropping image names
        :type regexps: list
        :param regexps_file: the text file with the regexps for dropping image names (one per line)
        :type regexps_file: str
        :param remove_ext: whether to remove the extension before determining matches
        :type remove_ext: bool
        :param invert: whether to invert the matching sense
        :type invert: bool
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.names = names
        self.names_file = names_file
        self.regexps = regexps
        self.regexps_file = regexps_file
        self.remove_ext = remove_ext
        self.invert = invert
        self._names = None
        self._regexps = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "discard-by-name"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Discards files based on list of image names and/or regular expressions that image names must match."

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION, DOMAIN_CLASSIFICATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData, ClassificationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData, ClassificationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--names", type=str, help="The image name(s) to drop.", required=False, nargs="*")
        parser.add_argument("-I", "--names_file", type=str, help="The text file with the image name(s) to drop.", required=False, default=None)
        parser.add_argument("-r", "--regexps", type=str, help="The regular expressions for matching image name(s) to drop.", required=False, nargs="*")
        parser.add_argument("-R", "--regexps_file", type=str, help="The text file with regular expressions for matching image name(s) to drop.", required=False, default=None)
        parser.add_argument("-e", "--remove_ext", action="store_true", help="Whether to remove the extension (and dot) before matching.")
        parser.add_argument("-V", "--invert", action="store_true", help="Whether to invert the matching sense.")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.names = ns.names
        self.names_file = ns.names_file
        self.regexps = ns.regexps
        self.regexps_file = ns.regexps_file
        self.remove_ext = ns.remove_ext
        self.invert = ns.invert

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()

        if self.remove_ext is None:
            self.remove_ext = False
        if self.invert is None:
            self.invert = False

        # names
        self._names = set()
        if self.names is not None:
            self._names.update(self.names)
        if self.names_file is not None:
            with open(self.names_file) as fp:
                lines = fp.readlines()
                for line in lines:
                    line = line.strip()
                    if len(line) > 0:
                        self._names.add(line)
        self.logger().info("# names: %d" % len(self._names))

        # regexps
        self._regexps = list()
        if self.regexps is not None:
            for regexp in self.regexps:
                self._regexps.append(re.compile(regexp))
        if self.regexps_file is not None:
            with open(self.regexps_file) as fp:
                lines = fp.readlines()
                for line in lines:
                    line = line.strip()
                    if len(line) > 0:
                        self._regexps.append(re.compile(line))
        self.logger().info("# regexps: %d" % len(self._regexps))

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        # nothing to do?
        if (len(self._names) == 0) and (len(self._regexps) == 0):
            return data

        if not isinstance(data, MetaDataHandler):
            return data
        if not data.has_metadata():
            return data
        if "file" not in data.get_metadata():
            return data
        
        full_file_name = data.get_metadata()["file"] 
        file_name = os.path.basename(full_file_name)
        if self.remove_ext:
            file_name = os.path.splitext(file_name)[0]

        add = True

        # check against names
        if len(self._names) > 0:
            if file_name in self._names:
                if not self.invert:
                    self.logger().info("Skipping based on name match: %s" % full_file_name)
                    add = False
            else:
                if self.invert:
                    self.logger().info("Skipping based on no name match (invert): %s" % full_file_name)
                    add = False

        # check against regexps
        if add:
            for regexp in self._regexps:
                if regexp.fullmatch(file_name) is not None:
                    if not self.invert:
                        self.logger().info("Skipping based on regexp match: %s" % full_file_name)
                        add = False
                        break
                else:
                    if self.invert:
                        self.logger().info("Skipping based on no regexp match (invert): %s" % full_file_name)
                        add = False
                        break

        if add:
            return data
        else:
            return None
