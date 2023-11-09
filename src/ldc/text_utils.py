import re
import string
from typing import List, Tuple

from ldc.core import DEFAULT_END_CHARS, DEFAULT_QUOTE_CHARS


def prune_lines(lines: List[str], min_len: int = 1) -> List[str]:
    """
    Removes lines that only consist of too few characters.

    :param lines: the lines to prune
    :type lines: list
    :param min_len: the minimum length the line must have (after .strip() call)
    :type min_len: int
    :return: the pruned list
    :rtype: list
    """
    result = []
    for sentence in lines:
        if len(sentence.strip()) > min_len:
            result.append(sentence)

    return result


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

    prune_lines(result)

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

    result = prune_lines(result)

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

    result = prune_lines(result)

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
                parts = line.split()
                line = ""
                for part in parts:
                    if len(line) + len(part) + 1 <= max_length:
                        line += " " + part
                    else:
                        result.append(line.strip())
                        line = ""
                if len(line) > 0:
                    result.append(line)
                    line = ""
            else:
                result.append(line)
                line = ""
    return result


def remove_patterns(lines: List[str], expr_remove: List[str]) -> Tuple[List[str], int]:
    """
    Removes all lines that match the patterns (inline).

    :param lines: the lines to process
    :type lines: list
    :param expr_remove: the list of regular expression for removing substrings (uses re.sub(expr, "", line))
    :type expr_remove: list
    :return: the tuple of processed lines and counter of how many lines were affected
    :rtype: tuple
    """
    result = []
    affected = 0
    for i in range(len(lines)):
        new_line = lines[i]
        for expr in expr_remove:
            new_line = re.sub(expr, "", new_line)
        if len(lines[i]) != len(new_line):
            result.append(new_line)
            affected += 1
        else:
            result.append(lines[i])
    return result, affected


def remove_empty(lines: List[str]) -> List[str]:
    """
    Removes empty lines from the list and returns an updated list.

    :param lines: the lines to process
    :type lines: list
    :return: the updated list
    :rtype: list
    """
    result = []
    for line in lines:
        if len(line.strip()) > 0:
            result.append(line)
    return result


def remove_blocks(lines: List[str], block_removal_start: List[str], block_removal_end: List[str]) -> List[str]:
    """
    Removes blocks of text between the defined start/end strings (incl these strings).

    :param lines: the lines to process
    :type lines: list
    :param block_removal_start: the strings signifying the start of a block
    :type block_removal_start: list
    :param block_removal_end: the strings signifying the end of a block
    :type block_removal_end: list
    :return: the updated lines
    :rtype: list
    """
    result = []
    in_block = False

    for line in lines:
        if in_block:
            for end in block_removal_end:
                if end in line:
                    in_block = False
                    continue
        else:
            for start in block_removal_start:
                if start in line:
                    in_block = True
                    break
            if not in_block:
                result.append(line)

    return result


def replace_patterns(lines: List[str], find: List[str], replace: List[str]) -> Tuple[List[str], int]:
    """
    Replaces the regexp patterns with the replacement strings.

    :param lines: the lines to process
    :type lines: list
    :param find: the list of regular expression for finding substrings to replace (uses re.sub(find, replace, line))
    :type find: list
    :param replace: the list of replacement strings
    :type replace: list
    :return: the tuple of processed lines and counter of how many lines were affected
    :rtype: tuple
    """
    if len(find) != len(replace):
        raise Exception("Number of regexp to find strings and replacement strings differ: %d != %d" % (len(find), len(replace)))

    result = []
    affected = 0
    for i in range(len(lines)):
        new_line = lines[i]
        for n, f in enumerate(find):
            new_line = re.sub(f, replace[n], new_line)
        if lines[i] != new_line:
            result.append(new_line)
            affected += 1
        else:
            result.append(lines[i])
    return result, affected
