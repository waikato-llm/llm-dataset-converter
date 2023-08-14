from dataclasses import dataclass
from typing import Iterable, List

from ldc.core import PAIRS_DOMAIN
from ldc.io import Reader, Writer, StreamWriter, BatchWriter
from ldc.filter import Filter


@dataclass
class PairData:
    """
    Container for pair data.
    """
    instruction: str
    input: str
    output: str
    meta: dict

    @classmethod
    def parse(cls, d):
        """
        Obtains the data from the provided dictionary and creates a PairData instance.

        :param d: the dictionary to get the data from
        :type d: dict
        :return: the generated instance
        :rtype: PairData
        """
        return PairData(
            instruction=d.get("instruction", None),
            input=d.get("input", None),
            output=d.get("output", None),
            meta=None
        )

    def to_dict(self):
        """
        Returns its data as a dictionary.

        :return: the data a dictionary
        :rtype: dict
        """
        result = dict()
        atts = ["instruction", "input", "output"]
        for att in atts:
            value = getattr(self, att)
            if value is not None:
                result[att] = value
        return result


class PairReader(Reader):
    """
    Reader for pair data.
    """
    def domains(self) -> List[str]:
        """
        Returns the domains of the reader.

        :return: the domains
        :rtype: list
        """
        return [PAIRS_DOMAIN]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PairData]

    def read(self) -> Iterable[PairData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable
        """
        raise NotImplemented()


class PairWriter(Writer):
    """
    Writer for pair data.
    """

    def domains(self) -> List[str]:
        """
        Returns the domains of the writer.

        :return: the domains
        :rtype: list
        """
        return [PAIRS_DOMAIN]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData]


class StreamPairWriter(PairWriter, StreamWriter):
    """
    Stream writer for pair data.
    """

    def write_stream(self, data: PairData):
        """
        Saves the data one by one.

        :param data: the data to write
        :type data: PairData
        """
        raise NotImplemented()


class BatchPairWriter(PairWriter, BatchWriter):
    """
    Batch writer for pair data.
    """

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as list of PairData
        :type data: list
        """
        raise NotImplemented()


class PairFilter(Filter):
    """
    Filter for pair data.
    """

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [PAIRS_DOMAIN]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PairData]
