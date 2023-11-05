import abc
from dataclasses import dataclass
from typing import Iterable, List, Dict, Optional, Union

from ldc.core import DOMAIN_PAIRS, MetaDataHandler
from ldc.base_io import Reader, Writer, StreamWriter, BatchWriter
from ldc.filter import Filter

PAIRDATA_INSTRUCTION = "instruction"
PAIRDATA_INPUT = "input"
PAIRDATA_OUTPUT = "output"
PAIRDATA_FIELDS = [PAIRDATA_INSTRUCTION, PAIRDATA_INPUT, PAIRDATA_OUTPUT]


@dataclass
class PairData(MetaDataHandler):
    """
    Container for pair data.
    """
    instruction: str
    input: str
    output: str
    meta: dict = None

    def has_metadata(self) -> bool:
        """
        Returns whether meta-data is present.

        :return: True if meta-data present
        :rtype: bool
        """
        return self.meta is not None

    def get_metadata(self) -> Optional[Dict]:
        """
        Returns the meta-data.

        :return: the meta-data, None if not available
        :rtype: dict
        """
        return self.meta

    def set_metadata(self, metadata: Optional[Dict]):
        """
        Sets the meta-data to use.

        :param metadata: the new meta-data, can be None
        :type metadata: dict
        """
        self.meta = metadata

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
            if (value is None) and (att == "input"):
                value = ""
            if value is not None:
                result[att] = value
        return result


class PairReader(Reader, abc.ABC):
    """
    Reader for pair data.
    """
    def domains(self) -> List[str]:
        """
        Returns the domains of the reader.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS]

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
        raise NotImplementedError()


class PairWriter(Writer, abc.ABC):
    """
    Writer for pair data.
    """

    def domains(self) -> List[str]:
        """
        Returns the domains of the writer.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData]


class StreamPairWriter(PairWriter, StreamWriter, abc.ABC):
    """
    Stream writer for pair data.
    """

    def write_stream(self, data: Union[PairData, Iterable[PairData]]):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        """
        raise NotImplementedError()


class BatchPairWriter(PairWriter, BatchWriter, abc.ABC):
    """
    Batch writer for pair data.
    """

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PairData
        """
        raise NotImplementedError()


class PairFilter(Filter, abc.ABC):
    """
    Filter for pair data.
    """

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS]

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
