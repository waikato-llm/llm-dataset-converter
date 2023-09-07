import abc
from dataclasses import dataclass
from typing import Iterable, List

from ldc.core import DOMAIN_PRETRAIN, DEFAULT_END_CHARS
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
    

class PretrainReader(Reader, abc.ABC):
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
        raise NotImplementedError()


class PretrainWriter(Writer, abc.ABC):
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


class StreamPretrainWriter(PretrainWriter, StreamWriter, abc.ABC):
    """
    Stream writer for pretrain data.
    """

    def write_stream(self, data: PretrainData):
        """
        Saves the data one by one.

        :param data: the data to write
        :type data: PretrainData
        """
        raise NotImplementedError()


class BatchPretrainWriter(PretrainWriter, BatchWriter, abc.ABC):
    """
    Batch writer for pretrain data.
    """

    def write_batch(self, data: Iterable[PretrainData]):
        """
        Saves the data in one go.

        :param data: the data to write as list of PretrainData
        :type data: list
        """
        raise NotImplementedError()


class PretrainFilter(Filter, abc.ABC):
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


def split_into_sentences(lines: List[str], end_chars: str = DEFAULT_END_CHARS) -> List[str]:
    """
    Splits text lines into separate sentences.

    :param lines: the lines to process
    :type lines: list
    :param end_chars: the characters that end a sentence
    :type end_chars: str
    :return: the updated lines
    :rtype: list
    """
    result = []

    for line in lines:
        while len(line) > 0:
            pos = len(line)
            for c in end_chars:
                if c in line:
                    pos = min(pos, line.index(c))
            if pos < len(line):
                result.append(line[0:pos + 1].strip())
                line = line[pos + 1:].strip()
                # dangling char?
                if len(line) == 1:
                    result[-1] += line
                    line = ""
            else:
                result.append(line.strip())
                line = ""

    return result
