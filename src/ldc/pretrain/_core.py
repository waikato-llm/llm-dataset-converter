from dataclasses import dataclass
from typing import Iterable, List

from ldc.core import DOMAIN_PRETRAIN
from ldc.io import Reader, Writer, StreamWriter, BatchWriter
from ldc.filter import Filter


@dataclass
class PretrainData:
    """
    Container for pretrain data.
    """
    content: str
    meta: dict = None

    @classmethod
    def parse(cls, d: dict) -> 'PretrainData':
        """
        Obtains the data from the provided dictionary and creates a PretrainData instance.

        :param d: the dictionary to get the data from
        :type d: dict
        :return: the generated instance
        :rtype: PretrainData
        """
        return PretrainData(
            content=d.get("content", None),
        )

    def to_dict(self) -> dict:
        """
        Returns its data as a dictionary.

        :return: the data a dictionary
        :rtype: dict
        """
        return {
            "content": self.content,
        }
    

class PretrainReader(Reader):
    """
    Reader for pretrain data.
    """
    def domains(self) -> List[str]:
        """
        Returns the domains of the reader.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PRETRAIN]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PretrainData]

    def read(self) -> Iterable[PretrainData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable
        """
        raise NotImplemented()


class PretrainWriter(Writer):
    """
    Writer for pretrain data.
    """

    def domains(self) -> List[str]:
        """
        Returns the domains of the writer.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PRETRAIN]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PretrainData]


class StreamPretrainWriter(PretrainWriter, StreamWriter):
    """
    Stream writer for pretrain data.
    """

    def write_stream(self, data: PretrainData):
        """
        Saves the data one by one.

        :param data: the data to write
        :type data: PretrainData
        """
        raise NotImplemented()


class BatchPretrainWriter(PretrainWriter, BatchWriter):
    """
    Batch writer for pretrain data.
    """

    def write_batch(self, data: Iterable[PretrainData]):
        """
        Saves the data in one go.

        :param data: the data to write as list of PretrainData
        :type data: list
        """
        raise NotImplemented()


class PretrainFilter(Filter):
    """
    Filter for pretrain data.
    """

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PRETRAIN]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PretrainData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PretrainData]

