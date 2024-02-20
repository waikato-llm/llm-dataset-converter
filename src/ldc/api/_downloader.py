import abc

from wai.logging import LOGGING_WARNING
from seppl import PluginWithLogging, Initializable


class Downloader(PluginWithLogging, Initializable, abc.ABC):
    """
    Base class for downloader classes.
    """

    def __init__(self, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the handler.

        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)

    def download(self):
        """
        Performs the download.
        """
        raise NotImplementedError()
