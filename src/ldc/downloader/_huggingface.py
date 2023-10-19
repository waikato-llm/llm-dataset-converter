import argparse
from typing import List, Union

from ldc.core import LOGGING_WARN
from ._core import Downloader

from huggingface_hub import hf_hub_download, snapshot_download
from huggingface_hub.constants import REPO_TYPES


class Huggingface(Downloader):
    """
    Downloader for Huggingface files and datasets.
    """

    def __init__(self, repo_id: str = None, repo_type: str = None, filename: Union[str, List[str]] = None,
                 revision: str = None, output_dir: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the downloader.

        :param repo_id: the ID of the repository/dataset to download
        :type repo_id: str
        :param repo_type: the type of the repository, see REPO_TYPES
        :type repo_type: str
        :param filename: when only to download specific file(s) rather than the whole dataset
        :type filename: str or list
        :param revision: the revision of the dataset, None for latest
        :type revision: str
        :param output_dir: the directory to store the data in, None for default Hugging Face cache dir
        :type output_dir: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.repo_id = repo_id
        self.repo_type = repo_type
        self.filename = filename
        self.revision = revision 
        self.output_dir = output_dir

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "huggingface"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "For downloading files and datasets from Huggingface (https://huggingface.co/)."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--repo_id", help="The name of the Hugging Face repository/dataset to download", required=True)
        parser.add_argument("-t", "--repo_type", help="The type of the repository", choices=REPO_TYPES, default=None, required=False)
        parser.add_argument("-f", "--filename", help="The name of the file to download rather than the full dataset", default=None, required=False, nargs="*")
        parser.add_argument("-r", "--revision", help="The revision of the dataset to download, omit for latest", default=None, required=False)
        parser.add_argument("-o", "--output_dir", help="The directory to store the data in, stores it in the default Hugging Face cache directory when omitted.", default=None, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.repo_id = ns.repo_id
        self.repo_type = ns.repo_type
        self.filename = ns.filename
        self.revision = ns.revision 
        self.output_dir = ns.output_dir

    def initialize(self):
        """
        Initializes the downloading.
        """
        super().initialize()
        if (self.repo_id is None) or (len(self.repo_id) == 0):
            raise Exception("No repo_id provided to download from!")

    def download(self):
        """
        Performs the download.
        """
        if isinstance(self.filename, str):
            filename = [self.filename]
        else:
            filename = self.filename

        self.logger().info("Repository ID: %s" % self.repo_id)
        if self.repo_type is not None:
            self.logger().info("Repository type: %s" % self.repo_type)
        if filename is not None:
            self.logger().info("Filename(s): %s" % ", ".join(filename))
        self.logger().info("Revision: %s" % ("latest" if (self.revision is None) else self.revision))
        self.logger().info("Output: %s" % ("default cache dir" if (self.output_dir is None) else self.output_dir))

        if filename is None:
            path = snapshot_download(self.repo_id, revision=self.revision, local_dir=self.output_dir,
                                     repo_type=self.repo_type, local_dir_use_symlinks=False)
            self.logger().info("Downloaded: %s" % path)
        else:
            for f in filename:
                path = hf_hub_download(self.repo_id, filename=f, revision=self.revision, local_dir=self.output_dir,
                                       repo_type=self.repo_type, local_dir_use_symlinks=False)
                self.logger().info("Downloaded: %s" % path)
