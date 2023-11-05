import argparse
from typing import List

from ldc.core import LOGGING_WARN, CommandlineHandler, DOMAIN_ANY
from ldc.base_io import Writer, BatchWriter, StreamWriter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData
from seppl import split_args, split_cmdline, Plugin
from ._core import Filter, MultiFilter


class Tee(Filter):
    """
    Forwards the data coming through to the sub-flow.
    """

    def __init__(self, sub_flow: List[CommandlineHandler] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param sub_flow: the filter(s)/writer to forward the data to
        :type sub_flow: list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.sub_flow = sub_flow
        self._filter = None
        self._writer = None
        self._data_buffer = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "tee"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Forwards the data passing through to the filter/writer defined as its sub-flow."

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
        parser.add_argument("-f", "--sub_flow", type=str, default=None, help="The command-line defining the subflow (filter(s)/writer).")
        return parser

    def _parse_commandline(self, cmdline: str) -> List[Plugin]:
        """
        Parses the command-line and returns the list of plugins it represents.
        Raises an exception in case of an invalid sub-flow.
        
        :param cmdline: the command-line to parse
        :type cmdline: str 
        :return: 
        """
        from ldc.registry import available_filters, available_writers
        from seppl import args_to_objects

        # split command-line into valid plugin subsets
        valid = dict()
        valid.update(available_filters())
        valid.update(available_writers())
        args = split_args(split_cmdline(cmdline), list(valid.keys()))
        return args_to_objects(args, valid, allow_global_options=False)

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.sub_flow = None
        if ns.sub_flow is not None:
            self.sub_flow = self._parse_commandline(ns.sub_flow)

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()

        if self.sub_flow is None:
            self.sub_flow = []

        if len(self.sub_flow) > 0:
            self._filter = None
            self._writer = None
            filters = []
            for plugin in self.sub_flow:
                if isinstance(plugin, Filter):
                    filters.append(plugin)
                elif isinstance(plugin, Writer):
                    self._writer = plugin
                    # no more plugins allowed beyond writer
                    break
            if len(filters) == 1:
                self._filter = filters[0]
            elif len(filters) > 1:
                self._filter = MultiFilter(filters=filters)
            if (self._writer is not None) and isinstance(self._writer, BatchWriter):
                self._data_buffer = []

        if self._filter is not None:
            self._filter.session = self.session
        if self._writer is not None:
            self._writer.session = self.session

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data

        # filter data
        if self._filter is not None:
            data = self._filter.process(data)

        # write data
        if (data is not None) and (self._writer is not None):
            if isinstance(self._writer, BatchWriter):
                self._data_buffer.append(data)
            elif isinstance(self._writer, StreamWriter):
                self._writer.write_stream(data)
            else:
                raise Exception("Unhandled type of writer: %s" % str(type(self._writer)))

        return result

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()

        # flush batch buffer
        if (self._data_buffer is not None) and isinstance(self._writer, BatchWriter):
            self.logger().info("Flushing data buffer...")
            self._writer.write_batch(self._data_buffer)
            self._data_buffer = None

        # finalize sub-flow
        if self._filter is not None:
            self._filter.finalize()
        if self._writer is not None:
            self._writer.finalize()
