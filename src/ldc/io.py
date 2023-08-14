from typing import Iterable

from ldc.core import CommandlineHandler, OutputProducer, InputConsumer


class Reader(CommandlineHandler, OutputProducer):
    """
    Ancestor of classes that read data.
    """

    def read(self) -> Iterable:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable
        """
        raise NotImplemented()


class Writer(CommandlineHandler, InputConsumer):
    """
    Ancestor of classes that write data.
    """
    pass


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
