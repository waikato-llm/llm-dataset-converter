import abc
import bz2
import logging

import chardet
import gzip
import lzma
import os
import pyzstd
import seppl.io

from typing import Iterable, Optional

from ldc.core import DomainHandler
from wai.logging import LOGGING_WARNING


COMPRESSION_BZIP2 = "bz2"
COMPRESSION_GZIP = "gz"
COMPRESSION_XZ = "xz"
COMPRESSION_ZSTD = "zstd"
COMPRESSION_FORMATS = [
    COMPRESSION_BZIP2,
    COMPRESSION_GZIP,
    COMPRESSION_XZ,
    COMPRESSION_ZSTD,
]


DEFAULT_ENCODING_MAX_CHECK_LENGTH = 1024 * 10
""" the maximum number of bytes to read for determining the encoding. """

ENV_ENCODING_MAX_CHECK_LENGTH = "LDC_ENCODING_MAX_CHECK_LENGTH"
""" the environment variable to use for overriding the max check length for determining the file encoding. """

ENCODING_MAX_CHECK_LENGTH = None
""" the determined max check length for determining the file encoding. """


def encoding_max_check_length() -> int:
    """
    Returns the maximum number of bytes to use for determining the file encoding.
    See environment variable constant ENV_ENCODING_MAX_CHECK_LENGTH.

    :return: the number of bytes, -1 for whole file
    :rtype: int
    """
    global ENCODING_MAX_CHECK_LENGTH
    if ENCODING_MAX_CHECK_LENGTH is None:
        if ENV_ENCODING_MAX_CHECK_LENGTH in os.environ:
            try:
                ENCODING_MAX_CHECK_LENGTH = int(os.environ[ENV_ENCODING_MAX_CHECK_LENGTH])
            except:
                print("Failed to parsed env var '%s' as int: %s" % (ENV_ENCODING_MAX_CHECK_LENGTH, os.environ[ENV_ENCODING_MAX_CHECK_LENGTH]))
                ENCODING_MAX_CHECK_LENGTH = DEFAULT_ENCODING_MAX_CHECK_LENGTH
        else:
            ENCODING_MAX_CHECK_LENGTH = DEFAULT_ENCODING_MAX_CHECK_LENGTH
    return ENCODING_MAX_CHECK_LENGTH


def determine_encoding(path: str, max_check_length: int = None) -> Optional[str]:
    """
    Determines the file encoding of the text file.

    :param path: the file to determine the encoding for
    :type path: str
    :param max_check_length: the maximum number of bytes to use for determining the encoding, -1 for all
    :type max_check_length: int
    :return: the encoding, None if file does not exist
    :rtype: str
    """
    if os.path.exists(path):
        if max_check_length is None:
            max_check_length = encoding_max_check_length()
        raw = open(path, "rb").read(max_check_length)
        result = chardet.detect(raw)["encoding"]
        # use utf-8 over ascii
        if result == "ascii":
            result = "utf-8"
        return result
    else:
        return None


def is_compressed(path: str):
    """
    Returns whether the file represents a compression that we can handle,
    based on the file extension: .gz, bz2, .xz, .zst/.zstd

    :param path: the file to check
    :type path: str
    :return: True if supported compression
    """
    path_lc = path.lower()
    if path_lc.endswith(".gz"):
        return True
    elif path_lc.endswith(".bz2"):
        return True
    elif path_lc.endswith(".xz"):
        return True
    elif path_lc.endswith(".zst") or path_lc.endswith(".zstd"):
        return True
    else:
        return False


def remove_compression_suffix(path: str) -> str:
    """
    Removes the compression suffix from the file.

    :param path: the path to remove the suffix from
    :type path: str
    :return: the cleaned up path
    :rtype: str
    """
    if is_compressed(path):
        return os.path.splitext(path)[0]
    else:
        return path


def replace_extension(path: str, ext: str) -> str:
    """
    Replaces the current extension of the file with the new one.
    Automatically removes any compression suffix first.

    :param path: the file to replace the extension for
    :type path: str
    :param ext: the new extension to use (incl dot)
    :type ext: str
    :return: the updated filename
    :rtype: str
    """
    result = remove_compression_suffix(path)
    result = os.path.splitext(result)[0] + ext
    return result


def open_file(path: str, mode: str = None, encoding: str = None, compression: str = None, logger: logging.Logger = None):
    """
    Opens the file and returns a file-like object.
    Automatically decompresses: .gz, bz2, .xz, .zst/.zstd

    :param path: the file to open
    :type path: str
    :param mode: the mode to use for opening the file
    :type mode: str
    :param encoding: the encoding to use, use None for default
    :type encoding: str
    :param compression: the explicit compression to use (gz/bz2/xz/zstd)
    :type compression: str
    :param logger: the optional logger to use for outputting auto-determined encoding
    :type logger: str
    :return: the file-like object
    """
    path_lc = path.lower()
    if path_lc.endswith(".gz") or (compression == COMPRESSION_GZIP):
        return gzip.open(path, mode=mode, encoding=encoding)
    elif path_lc.endswith(".bz2") or (compression == COMPRESSION_BZIP2):
        return bz2.open(path, mode=mode, encoding=encoding)
    elif path_lc.endswith(".xz") or (compression == COMPRESSION_XZ):
        return lzma.open(path, mode=mode, encoding=encoding)
    elif path_lc.endswith(".zst") or path_lc.endswith(".zstd") or (compression == COMPRESSION_ZSTD):
        return pyzstd.open(path, mode=mode, encoding=encoding)
    else:
        if compression is not None:
            raise Exception("Unhandled compression: %s" % compression)
        else:
            if encoding is None:
                encoding = determine_encoding(path)
                if logger is not None:
                    logger.info("Auto-determined encoding '%s' for %s" % (str(encoding), path))
            return open(path, mode=mode, encoding=encoding)


def generate_output(input_path: str, output_path: str, ext: str, compression: Optional[str]) -> str:
    """
    Generates a new output filename based on the current input, the output and extension.
    If the output path is not a directory, simply returns that.
    If the output path is a directory, it will construct a filename base on the
    output dir and the input filename (with a new extension).

    :param input_path: the input filename to generate an output filename for
    :type input_path: str
    :param output_path: the output filename/dir to use
    :type output_path: str
    :param ext: the extension to use
    :type ext: str
    :param compression: the compression to use, None or empty string for no compression
    :type compression: str
    :return: the generated output file
    :rtype: str
    """
    if compression is None:
        compression = ""
    elif len(compression) > 0:
        compression = "." + compression
    if os.path.isdir(output_path):
        base = os.path.basename(replace_extension(input_path, ext + compression))
        return os.path.join(output_path, base)
    else:
        return output_path


class Reader(seppl.io.Reader, seppl.Initializable, DomainHandler, abc.ABC):
    """
    Ancestor of classes that read data.
    """

    def __init__(self, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the handler.

        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)


class StreamWriter(seppl.io.StreamWriter, seppl.Initializable, DomainHandler, abc.ABC):
    """
    Ancestor for classes that write data one record at a time.
    """

    def write_stream(self, data):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        """
        raise NotImplementedError()

    def _output_needs_changing(self, current_output: str, target: str, ext: str) -> bool:
        """
        Checks whether the output needs changing.

        :param current_output: the current output
        :type current_output: str
        :param target: the output target
        :type target: str
        :param ext: the extension for the output file, incl dot
        :type ext: str
        :return: True if the output needs to change
        :rtype: bool
        """
        if current_output is None:
            return True
        output = generate_output(self.session.current_input, target, ext, self.session.options.compression)
        if current_output != output:
            return True
        return False


class BatchWriter(seppl.io.BatchWriter, seppl.Initializable, DomainHandler, abc.ABC):
    """
    Ancestor of classes that write data all at once.
    """

    def write_batch(self, data: Iterable):
        """
        Saves the data in one go.

        :param data: the data to write
        :type data: Iterable
        """
        raise NotImplementedError()

    def _output_needs_changing(self, current_output: str, target: str, ext: str) -> bool:
        """
        Checks whether the output needs changing.

        :param current_output: the current output
        :type current_output: str
        :param target: the output target
        :type target: str
        :param ext: the extension for the output file, incl dot
        :type ext: str
        :return: True if the output needs to change
        :rtype: bool
        """
        if current_output is None:
            return True
        output = generate_output(self.session.current_input, target, ext, self.session.options.compression)
        if current_output != output:
            return True
        return False
