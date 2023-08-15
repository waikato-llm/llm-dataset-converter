from typing import List

from ldc.core import CommandlineHandler, InputConsumer, OutputProducer, SessionHandler, Session, ANY_DOMAIN


class Filter(CommandlineHandler, InputConsumer, OutputProducer, SessionHandler):
    """
    Base class for filters.
    """

    def __init__(self, verbose: bool = False):
        """
        Initializes the handler.

        :param verbose: whether to be more verbose in the output
        :type verbose: bool
        """
        super().__init__(verbose=verbose)
        self._session = None

    @property
    def session(self) -> Session:
        """
        Returns the current session object

        :return: the session object
        :rtype: Session
        """
        return self._session

    @session.setter
    def session(self, s: Session):
        """
        Sets the session object to use.

        :param s: the session object
        :type s: Session
        """
        self._session = s

    def keep(self, data) -> bool:
        """
        Whether to keep the data record or not.

        :param data: the record to check
        :return: True if to keep
        :rtype: bool
        """
        raise NotImplemented()


class MultiFilter(Filter):
    """
    Combines multiple filters.
    """

    def __init__(self, filters: List[Filter], verbose: bool = False):
        """
        Initialize with the specified filters.

        :param filters: the filters to use
        :type filters: list
        :param verbose: whether to be more verbose in the output
        :type verbose: bool
        """
        super().__init__(verbose=verbose)
        self.filters = filters[:]

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "multi-filter"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Combines multiple filters."

    def domains(self) -> List[str]:
        """
        Returns the domain of the handler.

        :return: the domain
        :rtype: str
        """
        return [ANY_DOMAIN]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        if len(self.filters) > 0:
            return self.filters[0].accepts()
        else:
            return list()

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        if len(self.filters) > 0:
            return self.filters[-1].accepts()
        else:
            return list()

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        for f in self.filters:
            f.session = self.session

    def keep(self, data):
        """
        Whether to keep the data record or not.

        :param data: the record to check
        :return: True if to keep
        """
        result = True
        for f in self.filters:
            if not f.keep(data):
                result = False
                break
        return result