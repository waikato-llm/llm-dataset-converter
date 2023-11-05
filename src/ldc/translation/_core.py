import abc
from dataclasses import dataclass
from typing import Iterable, List, Dict, Optional, Union

from ldc.core import DOMAIN_TRANSLATION, MetaDataHandler
from ldc.base_io import Reader, Writer, StreamWriter, BatchWriter
from ldc.filter import Filter


@dataclass
class TranslationData(MetaDataHandler):
    """
    Container for pretrain data.
    """
    translations: dict  # lookup: language -> text
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
    def parse(cls, d: dict) -> 'TranslationData':
        """
        Obtains the data from the provided dictionary and creates a TranslationData instance.

        :param d: the dictionary to get the data from
        :type d: dict
        :return: the generated instance
        :rtype: TranslationData
        """
        return TranslationData(
            translations=d.get("translations", None),
        )

    def to_dict(self) -> dict:
        """
        Returns its data as a dictionary.

        :return: the data a dictionary
        :rtype: dict
        """
        return {
            "translations": self.translations,
        }
    

class TranslationReader(Reader, abc.ABC):
    """
    Reader for pretrain data.
    """
    def domains(self) -> List[str]:
        """
        Returns the domains of the reader.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_TRANSLATION]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [TranslationData]

    def read(self) -> Iterable[TranslationData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable
        """
        raise NotImplementedError()


class TranslationWriter(Writer, abc.ABC):
    """
    Writer for pretrain data.
    """

    def domains(self) -> List[str]:
        """
        Returns the domains of the writer.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_TRANSLATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [TranslationData]


class StreamTranslationWriter(TranslationWriter, StreamWriter, abc.ABC):
    """
    Stream writer for pretrain data.
    """

    def write_stream(self, data: Union[TranslationData, Iterable[TranslationData]]):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        """
        raise NotImplementedError()


class BatchTranslationWriter(TranslationWriter, BatchWriter, abc.ABC):
    """
    Batch writer for pretrain data.
    """

    def write_batch(self, data: Iterable[TranslationData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of TranslationData
        """
        raise NotImplementedError()


class TranslationFilter(Filter, abc.ABC):
    """
    Filter for pretrain data.
    """

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_TRANSLATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [TranslationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [TranslationData]
