import argparse
import copy
import json

from wai.logging import LOGGING_WARNING
from ._core import ClassificationData, ClassificationFilter


class ClassificationLabelMap(ClassificationFilter):
    """
    Generates a label string/int map and can also replace the label with the integer index.
    """

    def __init__(self, label_map: str = None, update_label: bool = False, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param label_map: the JSON file to store the label map in
        :type label_map: str
        :param update_label: whether to update the records, ie using the integer label index instead
        :type update_label: bool
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.label_map = label_map
        self.update_label = update_label
        self._mapping = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "classification-label-map"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Generates a label string/int map and can also replace the label with the integer index."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-L", "--label_map", type=str, help="The JSON file to store the label map in.", default=None, required=False)
        parser.add_argument("-u", "--update_label", action="store_true", help="Whether to the string labels with the integer index.", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.label_map = ns.label_map
        self.update_label = ns.update_label

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._mapping = dict()

    def _do_process(self, data: ClassificationData):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data

        # add label if missing
        if data.label not in self._mapping:
            self._mapping[data.label] = len(self._mapping)

        if self.update_label:
            meta = None
            if data.has_metadata():
                meta = copy.deepcopy(data.get_metadata())
            result = ClassificationData(text=data.text, label=self._mapping[data.label], meta=meta)

        return result

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        if self.label_map is None:
            self.logger().info("label map:\n%s" % json.dumps(self._mapping))
        else:
            with open(self.label_map, "w") as fp:
                json.dump(self._mapping, fp, indent=2)
