import argparse
import logging
import os
import re
import sys
import traceback
from typing import List

from ldc.core import init_logging, set_logging_level, LOGGING_WARN, LOGGING_LEVELS
from ldc.utils import Splitter

FIND = "llm-find"

_logger = logging.getLogger(FIND)


def _find(path: str, recursive: bool, match: List[str], not_match: List[str], files: List[str]):
    """
    Locates files in the specified input directory and adds the matches to the files list.

    :param path: the directory to scan
    :type path: str
    :param recursive: whether to scan the dir(s) recursively
    :type recursive: bool
    :param match: the list regexp that the full paths of the files must match in order to be included (None: includes all)
    :type match: list
    :param not_match: the regexp that the full paths of the files must match in order to be excluded (None: includes all)
    :type not_match: list
    :param files: the list to add the matching files to
    :type files: list
    """
    _logger.info("Entering: %s" % path)
    for f in os.listdir(path):
        if (f == ".") or (f == ".."):
            continue

        full = os.path.join(path, f)

        # dir?
        if os.path.isdir(full):
            if recursive:
                _find(full, recursive, match, not_match, files)
                _logger.info("Back to: %s" % path)
            else:
                continue

        # match?
        is_match = True
        if match is not None:
            for pattern in match:
                if re.search(pattern, full) is None:
                    is_match = False
                    break
        if is_match and (not_match is not None):
            for pattern in not_match:
                if re.search(pattern, full) is not None:
                    is_match = False
                    break
        if is_match:
            files.append(full)


def find_files(paths: List[str], output: str, recursive=False,
               match: List[str] = None, not_match: List[str] = None,
               split_ratios: List[int] = None, split_names: List[str] = None,
               split_name_separator: str = "-"):
    """
    Finds the files in the dir(s) and stores the full paths in text file(s).

    :param paths: the dir(s) to scan for files
    :type paths: list
    :param output: the output file to store the files in; when splitting, the split names get used as suffix (before .ext)
    :type output: str
    :param recursive: whether to scan the dir(s) recursively
    :type recursive: bool
    :param match: the list regexp that the full paths of the files must match in order to be included (None: includes all)
    :type match: list
    :param not_match: the regexp that the full paths of the files must match in order to be excluded (None: includes all)
    :type not_match: list
    :param split_ratios: the list of (int) ratios to use for splitting (must sum up to 100)
    :type split_ratios: list
    :param split_names: the list of suffixes to use for the splits
    :type split_names: list
    :param split_name_separator: the separator to use between file name and split name
    :type split_name_separator: str
    """
    # locate
    all_files = []
    for d in paths:
        _find(d, recursive, match, not_match, all_files)
    _logger.info("# files found: %d" % len(all_files))

    # split?
    if (split_ratios is not None) or (split_names is not None):
        splitter = Splitter(split_ratios, split_names)
        splitter.initialize()
        # generate output names
        split_output = dict()
        parts = os.path.splitext(output)
        for name in split_names:
            split_output[name] = parts[0] + split_name_separator + name + parts[1]
        # split the files
        split_files = dict()
        for name in split_names:
            split_files[name] = []
        for f in all_files:
            split_files[splitter.next()].append(f)
        for name in split_names:
            _logger.info("# files in split '%s': %d" % (name, len(split_files[name])))
        # write files
        for name in split_names:
            _logger.info("Writing files to: %s" % split_output[name])
            with open(split_output[name], "w") as fp:
                for f in split_files[name]:
                    fp.write(f)
                    fp.write("\n")
    else:
        _logger.info("Writing files to: %s" % output)
        with open(output, "w") as fp:
            for f in all_files:
                fp.write(f)
                fp.write("\n")


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    init_logging()
    parser = argparse.ArgumentParser(
        description="Tool for locating files in directories that match certain patterns and store them in files.",
        prog=FIND,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", metavar="DIR", help="The dir(s) to scan for files.", default=None, type=str, required=True, nargs="+")
    parser.add_argument("-r", "--recursive", action="store_true", help="Whether to search the directories recursively", required=False)
    parser.add_argument("-o", "--output", metavar="FILE", help="The file to store the located file names in", type=str, required=True)
    parser.add_argument("-m", "--match", metavar="REGEXP", help="The regular expression that the (full) file names must match to be included", default=None, type=str, required=False, nargs="*")
    parser.add_argument("-n", "--not-match", metavar="REGEXP", help="The regular expression that the (full) file names must match to be excluded", default=None, type=str, required=False, nargs="*")
    parser.add_argument("--split_ratios", type=int, default=None, help="The split ratios to use for generating the splits (int; must sum up to 100)", nargs="*")
    parser.add_argument("--split_names", type=str, default=None, help="The split names to use as filename suffixes for the generated splits (before .ext)", nargs="*")
    parser.add_argument("--split_name_separator", type=str, default="-", help="The separator to use between file name and split name", required=False)
    parser.add_argument("-l", "--logging_level", choices=LOGGING_LEVELS, default=LOGGING_WARN, help="The logging level to use")
    parsed = parser.parse_args(args=args)
    set_logging_level(_logger, parsed.logging_level)
    find_files(parsed.input, parsed.output, recursive=parsed.recursive,
               match=parsed.match, not_match=parsed.not_match,
               split_ratios=parsed.split_ratios, split_names=parsed.split_names,
               split_name_separator=parsed.split_name_separator)


def sys_main() -> int:
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    """
    try:
        main()
        return 0
    except Exception:
        traceback.print_exc()
        print("options: %s" % str(sys.argv[1:]), file=sys.stderr)
        return 1


if __name__ == '__main__':
    main()
