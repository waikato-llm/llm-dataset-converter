import argparse
import logging
import os
import sys
import traceback

from typing import List

from ldc.core import init_logging, set_logging_level, LOGGING_WARN, LOGGING_LEVELS
from ldc.base_io import locate_files

PASTE = "llm-paste"

PH_TAB = "{T}"

_logger = logging.getLogger(PASTE)


def combine(input_files: List[str], output_file: str = None, separators: List[str] = None):
    """
    Combines the input (text) files side by side.

    :param input_files: the files to place side by side
    :type input_files: str
    :param output_file: the file to store the result in, prints to stdout if None
    :type output_file: str
    :param separators: the separators (one between each file) to use instead of default tab
    :type separators: str
    """
    if len(input_files) >= 10:
        input_files_info = "%d files" % len(input_files)
    else:
        input_files_info = ", ".join(input_files)
    _logger.info("Input files: %s" % input_files_info)
    if output_file is not None:
        _logger.info("Output file: %s" % output_file)
    if separators is not None:
        _logger.info("Separators: %s" % ", ".join(separators))

    # prepare separators
    if separators is None:
        separators = list()
        for i in range(len(input_files) - 1):
            separators.append("\t")
    else:
        if len(separators) < len(input_files) - 1:
            raise Exception("%d separators need to be defined for %d input files, but only got %d!"
                            % (len(input_files) - 1, len(input_files), len(separators)))
        for i in range(len(separators)):
            if separators[i] == PH_TAB:
                separators[i] = "\t"

    # open input files
    input_fps = list()
    can_read = list()
    for input_file in input_files:
        _logger.info("Opening: %s" % input_file)
        input_fps.append(open(input_file, "r"))
        can_read.append(True)

    # output
    if (output_file is None) or os.path.isdir(output_file):
        output = sys.stdout
    else:
        _logger.info("Opening: %s" % output_file)
        output = open(output_file, "w")

    # process files
    keep_reading = True
    count = 0
    while keep_reading:
        count += 1
        combined = ""
        for i in range(len(input_fps)):
            line = ""
            if can_read[i]:
                try:
                    line = input_fps[i].readline()
                    if len(line) == 0:
                        can_read[i] = False
                    if line.endswith("\n"):
                        line = line[0:len(line)-1]
                    if line.endswith("\r"):
                        line = line[0:len(line) - 1]
                except:
                    can_read[i] = False
            # combine
            if i > 0:
                combined += separators[i - 1]
            combined += line

        # anything else to read?
        keep_reading = False
        for i in range(len(can_read)):
            if can_read[i]:
                keep_reading = True
                break

        # output
        if keep_reading:
            output.write(combined)
            output.write("\n")

        # progress
        if (count % 1000) == 0:
            _logger.info("%d lines processed" % count)

    _logger.info("%d lines processed in total" % count)

    # close input files
    for input_file, input_fp in zip(input_files, input_fps):
        _logger.info("Closing: %s" % input_file)
        input_fp.close()

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
        description="Tool for combining multiple text files by placing them side-by-side.",
        prog=PASTE,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", type=str, help="Path to the text file(s) to combine; glob syntax is supported", required=False, nargs="*")
    parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the data files to combine", required=False, nargs="*")
    parser.add_argument("-o", "--output", metavar="FILE", help="The path of the file to store the combined data in; outputs it to stdout if omitted or a directory", default=None, type=str, required=False)
    parser.add_argument("-s", "--separator", metavar="SEP", help="The separators to use between the files; uses TAB if not supplied; use '" + PH_TAB + "' as placeholder for tab", default=None, type=str, required=False, nargs="*")
    parser.add_argument("-l", "--logging_level", choices=LOGGING_LEVELS, default=LOGGING_WARN, help="The logging level to use")
    parsed = parser.parse_args(args=args)
    set_logging_level(_logger, parsed.logging_level)
    input_files = locate_files(parsed.input, input_lists=parsed.input_list, fail_if_empty=True)
    combine(input_files=input_files, output_file=parsed.output, separators=parsed.separator)


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
