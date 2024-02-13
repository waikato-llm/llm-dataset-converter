import abc
from dataclasses import dataclass
from typing import Iterable, List, Dict, Optional, Union

from seppl import MetaDataHandler
from ldc.core import DOMAIN_CLASSIFICATION
from ldc.base_io import Reader, StreamWriter, BatchWriter
from ldc.filter import Filter

PAIRDATA_INSTRUCTION = "instruction"
PAIRDATA_INPUT = "input"
PAIRDATA_OUTPUT = "output"
PAIRDATA_FIELDS = [PAIRDATA_INSTRUCTION, PAIRDATA_INPUT, PAIRDATA_OUTPUT]


@dataclass
class ClassificationData(MetaDataHandler):
    """
    Container for classification data.
    """
    text: Optional[str]
    label: Optional[Union[str, int]]
    meta: Optional[dict] = None

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
        Obtains the data from the provided dictionary and creates a ClassificationData instance.

        :param d: the dictionary to get the data from
        :type d: dict
        :return: the generated instance
        :rtype: ClassificationData
        """
        return ClassificationData(
            text=d.get("text", None),
            label=d.get("label", None),
        )

    def to_dict(self):
        """
        Returns its data as a dictionary.

        :return: the data a dictionary
        :rtype: dict
        """
        result = dict()
        atts = ["text", "label"]
        for att in atts:
            value = getattr(self, att)
            if value is not None:
                result[att] = value
        return result


class ClassificationReader(Reader, abc.ABC):
    """
    Reader for classification data.
    """
    def domains(self) -> List[str]:
        """
        Returns the domains of the reader.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_CLASSIFICATION]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [ClassificationData]

    def read(self) -> Iterable[ClassificationData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable
        """
        raise NotImplementedError()


class StreamClassificationWriter(StreamWriter, abc.ABC):
    """
    Stream writer for classification data.
    """

    def domains(self) -> List[str]:
        """
        Returns the domains of the writer.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_CLASSIFICATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ClassificationData]

    def write_stream(self, data: Union[ClassificationData, Iterable[ClassificationData]]):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        """
        raise NotImplementedError()


class BatchClassificationWriter(BatchWriter, abc.ABC):
    """
    Batch writer for classification data.
    """

    def domains(self) -> List[str]:
        """
        Returns the domains of the writer.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_CLASSIFICATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ClassificationData]

    def write_batch(self, data: Iterable[ClassificationData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of ClassificationData
        """
        raise NotImplementedError()


class ClassificationFilter(Filter, abc.ABC):
    """
    Filter for classification data.
    """

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_CLASSIFICATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ClassificationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [ClassificationData]
