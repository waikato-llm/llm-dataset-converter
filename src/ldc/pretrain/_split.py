import copy

from ldc.core import LOGGING_WARN, domain_suffix
from ._core import PretrainData, PretrainFilter


class Split(PretrainFilter):
    """
    Splits pretrain text data into separate records on new lines. Automatically skips empty lines.
    """

    def __init__(self, logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "split-" + domain_suffix(self)

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Splits pretrain text data into separate records on new lines. Automatically skips empty lines."

    def _do_process(self, data: PretrainData):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        lines = data.content.split("\n")
        result = []
        for line in lines:
            if len(line.strip()) == 0:
                continue
            result.append(PretrainData(
                content=line,
                meta=copy.deepcopy(data.meta)
            ))

        self.logger().info("# lines -> # records: %d -> %d" % (len(lines), len(result)))

        return result
