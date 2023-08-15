import glob

from typing import Union, Iterable, List

from ldc.core import CommandlineHandler, OutputProducer, InputConsumer, Session, SessionHandler


def locate_files(inputs: Union[str, List[str]]) -> List[str]:
    """
    Locates all the files from the specified inputs, which may contain globs.

    :param inputs: the input path(s) with optional globs
    :type inputs: list
    :return: the expanded list of files
    :rtype: list
    """
    if isinstance(inputs, str):
        inputs = [inputs]
    elif isinstance(inputs, list):
        inputs = inputs
    else:
        raise Exception("Invalid inputs, must be string(s)!")

    result = []
    for inp in inputs:
        result.extend(glob.glob(inp))
    return result


class Reader(CommandlineHandler, OutputProducer, SessionHandler):
    """
    Ancestor of classes that read data.
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

    def read(self) -> Iterable:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable
        """
        raise NotImplemented()

    def has_finished(self) -> bool:
        """
        Returns whether reading has finished.

        :return: True if finished
        :rtype: bool
        """
        raise NotImplemented()


class Writer(CommandlineHandler, InputConsumer, SessionHandler):
    """
    Ancestor of classes that write data.
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


class StreamWriter(Writer):
    """
    Ancestor for classes that write data one record at a time.
    """

    def write_stream(self, data):
        """
        Saves the data one by one.

        :param data: the data to write
        """
        raise NotImplemented()


class BatchWriter(Writer):
    """
    Ancestor of classes that write data all at once.
    """

    def write_batch(self, data: Iterable):
        """
        Saves the data in one go.

        :param data: the data to write
        :type data: Iterable
        """
        raise NotImplemented()
