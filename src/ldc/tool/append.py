import argparse
import logging
import os
import sys
import traceback

from typing import List

from ldc.core import init_logging, set_logging_level, LOGGING_WARN, LOGGING_LEVELS
from ldc.base_io import locate_files

APPEND = "llm-append"

_logger = logging.getLogger(APPEND)


def combine(input_files: List[str], output_file: str = None):
    """
    Combines the input (text) files by appending them.

    :param input_files: the files to append
    :type input_files: str
    :param output_file: the file to store the result in, prints to stdout if None
    :type output_file: str
    """
    if len(input_files) >= 10:
        input_files_info = "%d files" % len(input_files)
    else:
        input_files_info = ", ".join(input_files)
    _logger.info("Input files: %s" % input_files_info)
    if output_file is not None:
        _logger.info("Output file: %s" % output_file)

    # output
    if (output_file is None) or os.path.isdir(output_file):
        output = sys.stdout
    else:
        _logger.info("Opening: %s" % output_file)
        output = open(output_file, "w")

    # append
    count = 0
    for input_file in input_files:
        with open(input_file, "r") as fp:
            for line in fp:
                count += 1
                output.write(line)
                # progress
                if (count % 1000) == 0:
                    _logger.info("%d lines processed" % count)

    _logger.info("%d lines processed in total" % count)

    # close output file
    if output_file is not None:
        _logger.info("Closing: %s" % output_file)
        output.close()


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    init_logging()
    parser = argparse.ArgumentParser(
        description="Tool for combining multiple text files by appending them.",
        prog=APPEND,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", type=str, help="Path to the text file(s) to append; glob syntax is supported", required=False, nargs="*")
    parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the data files to append", required=False, nargs="*")
    parser.add_argument("-o", "--output", metavar="FILE", help="The path of the file to store the combined data in; outputs it to stdout if omitted or a directory", default=None, type=str, required=False)
    parser.add_argument("-l", "--logging_level", choices=LOGGING_LEVELS, default=LOGGING_WARN, help="The logging level to use")
    parsed = parser.parse_args(args=args)
    set_logging_level(_logger, parsed.logging_level)
    input_files = locate_files(parsed.input, input_lists=parsed.input_list, fail_if_empty=True)
    combine(input_files=input_files, output_file=parsed.output)


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
