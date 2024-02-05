import argparse
import logging
import os
import sys
import traceback

from typing import List

from wai.logging import init_logging, set_logging_level, add_logging_level
from seppl.io import locate_files
from ldc.core import ENV_LLM_LOGLEVEL
from ldc.base_io import determine_encoding

FILE_ENCODING = "llm-file-encoding"

_logger = logging.getLogger(FILE_ENCODING)


def determine(input_files: List[str], max_check_length: int = None, output_file: str = None):
    """
    Determines the file encoding for the list of text files.

    :param input_files: the files to append
    :type input_files: str
    :param max_check_length: the maximum number of bytes to use for determining the file encoding, auto-mode if None
    :type max_check_length: int
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

    # determine
    for input_file in input_files:
        try:
            _logger.info("Checking: %s" % input_file)
            output.write(input_file)
            output.write("\n")
            enc = determine_encoding(input_file, max_check_length=max_check_length)
            output.write("    ")
            output.write(str(enc))
            output.write("\n")
        except:
            _logger.exception("Failed to determine file encoding of: %s" % input_file)

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
    init_logging(env_var=ENV_LLM_LOGLEVEL)
    parser = argparse.ArgumentParser(
        description="Tool for determining the file encoding of text files.",
        prog=FILE_ENCODING,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", type=str, help="Path to the text file(s) to check; glob syntax is supported", required=False, nargs="*")
    parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the actual files to check", required=False, nargs="*")
    parser.add_argument("-m", "--max_check_length", type=int, help="The maxmimum number of bytes to use for checking", required=False, default=None)
    parser.add_argument("-o", "--output", metavar="FILE", help="The path of the file to store the determined encodings in; outputs it to stdout if omitted or a directory", default=None, type=str, required=False)
    add_logging_level(parser)
    parsed = parser.parse_args(args=args)
    set_logging_level(_logger, parsed.logging_level)
    input_files = locate_files(parsed.input, input_lists=parsed.input_list, fail_if_empty=True)
    determine(input_files=input_files, max_check_length=parsed.max_check_length, output_file=parsed.output)


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
