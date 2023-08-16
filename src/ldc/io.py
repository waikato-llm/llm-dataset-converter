import bz2
import glob
import gzip
import lzma
import os
import pyzstd

from typing import Union, Iterable, List

from ldc.core import CommandlineHandler, OutputProducer, InputConsumer, Session, SessionHandler


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


def locate_files(inputs: Union[str, List[str]], fail_if_empty: bool = False) -> List[str]:
    """
    Locates all the files from the specified inputs, which may contain globs.

    :param inputs: the input path(s) with optional globs
    :type inputs: list
    :param fail_if_empty: whether to throw an exception if no files were located
    :type fail_if_empty: bool
    :return: the expanded list of files
    :rtype: list
    """
    if isinstance(inputs, str):
        inputs = [inputs]
    elif isinstance(inputs, list):
        inputs = inputs
    else:
        raise Exception("Invalid inputs, must be string(s)!")

    result = []
    for inp in inputs:
        result.extend(glob.glob(inp))

    if fail_if_empty and (len(result) == 0):
        raise Exception("Failed to locate any files using: %s" % str(inputs))

    return result


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


def remove_compression_suffix(path: str):
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


def open_file(path: str, mode: str = None, encoding: str = None, compression: str = None):
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
            return open(path, mode)


def generate_output(input_path: str, output_path: str, ext: str, compression: str) -> str:
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
    :param compression: the compression to use
    :type compression: str
    :return: the generated output file
    :rtype: str
    """
    if compression is None:
        compression = ""
    else:
        compression = "." + compression
    if os.path.isdir(output_path):
        if is_compressed(input_path):
            input_path = remove_compression_suffix(input_path)
        base = os.path.basename(input_path)
        return os.path.join(output_path, os.path.splitext(base)[0] + ext + compression)
    else:
        return input_path


class Reader(CommandlineHandler, OutputProducer, SessionHandler):
    """
    Ancestor of classes that read data.
    """

    def __init__(self, verbose: bool = False):
        """
        Initializes the handler.

        :param verbose: whether to be more verbose in the output
        :type verbose: bool
        """
        super().__init__(verbose=verbose)
        self._session = None

    @property
    def session(self) -> Session:
        """
        Returns the current session object

        :return: the session object
        :rtype: Session
        """
        return self._session

    @session.setter
    def session(self, s: Session):
        """
        Sets the session object to use.

        :param s: the session object
        :type s: Session
        """
        self._session = s

    def read(self) -> Iterable:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable
        """
        raise NotImplemented()

    def has_finished(self) -> bool:
        """
        Returns whether reading has finished.

        :return: True if finished
        :rtype: bool
        """
        raise NotImplemented()


class Writer(CommandlineHandler, InputConsumer, SessionHandler):
    """
    Ancestor of classes that write data.
    """

    def __init__(self, verbose: bool = False):
        """
        Initializes the handler.

        :param verbose: whether to be more verbose in the output
        :type verbose: bool
        """
        super().__init__(verbose=verbose)
        self._session = None

    @property
    def session(self) -> Session:
        """
        Returns the current session object

        :return: the session object
        :rtype: Session
        """
        return self._session

    @session.setter
    def session(self, s: Session):
        """
        Sets the session object to use.

        :param s: the session object
        :type s: Session
        """
        self._session = s


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
