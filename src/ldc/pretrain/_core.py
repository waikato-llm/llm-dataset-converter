import abc
from dataclasses import dataclass
import string
from typing import Iterable, List, Dict, Optional

from ldc.core import DOMAIN_PRETRAIN, DEFAULT_END_CHARS, DEFAULT_QUOTE_CHARS, MetaDataHandler
from ldc.io import Reader, Writer, StreamWriter, BatchWriter
from ldc.filter import Filter


@dataclass
class PretrainData(MetaDataHandler):
    """
    Container for pretrain data.
    """
    content: str
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


def assemble_preformatted(lines: List[str], end_chars: str = DEFAULT_END_CHARS,
                          quote_chars: str = DEFAULT_QUOTE_CHARS) -> List[str]:
    """
    Assembles preformatted lines into full sentences.

    :param lines: the lines to process
    :type lines: list
    :param end_chars: the characters that end a sentence
    :type end_chars: str
    :param quote_chars: the quote characters to use
    :type quote_chars: str
    :return: the updated lines
    :rtype: list
    """
    result = []
    new_sentence = False
    buffer = None

    for line in lines:
        line = line.strip()
        curr = line

        # remove quotes at end
        for c in quote_chars:
            if curr.endswith(c):
                curr = curr[:len(curr) - 1]

        # new sentence?
        if len(curr) == 0:
            new_sentence = True
        else:
            for c in end_chars:
                if curr.endswith(c):
                    new_sentence = True
                    break

        if new_sentence:
            new_sentence = False
            if len(line) > 0:
                if buffer is None:
                    buffer = line
                else:
                    buffer += " " + line
            if buffer is not None:
                result.append(buffer)
                buffer = None
        else:
            if buffer is None:
                buffer = line
            else:
                buffer += " " + line

    if buffer is not None:
        result.append(buffer)

    return result


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


def combine_sentences(sentences: List[str], max_sentences: int) -> List[str]:
    """
    Combines the lines (each representing a single sentence) into lines with at
    most the specified number of sentences.
    
    :param sentences: the sentences to combine
    :type sentences: list
    :param max_sentences: the maximum number of sentences per output line
    :type max_sentences: int
    :return: the new lines
    :rtype: list
    """
    if max_sentences <= 1:
        return sentences

    result = []
    current = []
    for sentence in sentences:
        if len(current) < max_sentences:
            # append full stop?
            if len(sentence.strip()) > 1:
                if sentence[-1] not in DEFAULT_END_CHARS:
                    sentence += "."
            current.append(sentence)
        else:
            result.append(" ".join(current))
            current = []

    if len(current) > 0:
        result.append(" ".join(current))

    return result


def find_word_boundary(s: str, pos: int, before: bool) -> int:
    """
    Finds the closest word boundary starting from the specified position.
    In the case that no whitespace/punctuation can be found, the initial position gets returned.

    :param s: the string to search
    :type s: str
    :param pos: the position to start the search for a whitespace on
    :type pos: int
    :param before: whether to look before or after the position for a word boundary
    :return: the position
    :rtype: int
    """
    result = pos

    if before:
        for i in range(pos, -1, -1):
            if (s[i] in string.whitespace) or (s[i] in string.punctuation):
                result = i
                break
    else:
        for i in range(pos, len(s)):
            if (s[i] in string.whitespace) or (s[i] in string.punctuation):
                result = i
                break

    return result


def apply_max_length(lines: List[str], max_length: int) -> List[str]:
    """
    Ensures that no line is longer than the specified maximum length.
    If a line should be longer, it is split at the word boundary below the limit.

    :param lines: the lines to process
    :type lines: list
    :param max_length: the maximum length for a line, <= 0 for unbounded
    :type max_length: int
    :return: the processed lines
    :rtype: int
    """
    if max_length <= 0:
        return lines

    result = []
    for line in lines:
        line = line.strip()
        while len(line) > 0:
            if len(line) > max_length:
                pos = find_word_boundary(line, max_length, True)
                result.append(line[:pos])
                line = line[pos:].strip()
            else:
                result.append(line)
                line = ""
    return result
