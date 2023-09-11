import abc
from typing import List

from ldc.core import CommandlineHandler, InputConsumer, OutputProducer, DomainHandler, SessionHandler, Session, DOMAIN_ANY
from ldc.core import LOGGING_WARN

FILTER_ACTION_KEEP = "keep"
FILTER_ACTION_DISCARD = "discard"
FILTER_ACTIONS = [FILTER_ACTION_KEEP, FILTER_ACTION_DISCARD]


class Filter(CommandlineHandler, InputConsumer, OutputProducer, DomainHandler, SessionHandler, abc.ABC):
    """
    Base class for filters.
    """

    def __init__(self, logging_level: str = LOGGING_WARN):
        """
        Initializes the handler.

        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self._session = None
        self._last_input = None

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

    def _has_input_changed(self, current_input: str = None, update: bool = False) -> bool:
        """
        Checks whether the current input is different from the last one we processed.

        :param current_input: the current input, uses the current_input from the session if None
        :type current_input: str
        :param update: whether to update the last input immediately
        :type update: bool
        :return: True if input has changed
        :rtype: bool
        """
        if current_input is None:
            current_input = self.session.current_input
        result = self._last_input != current_input
        if update:
            self._update_last_input(current_input)
        return result

    def _update_last_input(self, current_input: str):
        """
        Updates the last input that was processed.

        :param current_input: the "new" last input
        :type current_input: str
        """
        self._last_input = current_input

    def process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        raise NotImplementedError()


class MultiFilter(Filter):
    """
    Combines multiple filters.
    """

    def __init__(self, filters: List[Filter] = None, logging_level: str = LOGGING_WARN):
        """
        Initialize with the specified filters.

        :param filters: the filters to use
        :type filters: list
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.filters = None if (filters is None) else filters[:]

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
        return [DOMAIN_ANY]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        if (self.filters is not None) and (len(self.filters) > 0):
            return self.filters[0].accepts()
        else:
            return list()

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        if (self.filters is not None) and (len(self.filters) > 0):
            return self.filters[-1].generates()
        else:
            return list()

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        for f in self.filters:
            f.initialize()
            f.session = self.session

    def process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data
        for f in self.filters:
            result = f.process(result)
            if result is None:
                break
        return result

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        for f in self.filters:
            f.finalize()
