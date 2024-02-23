import argparse
import csv
import json
import logging
import os
import sys
import traceback

from typing import List

from wai.logging import init_logging, set_logging_level, add_logging_level
from seppl.io import locate_files
from ldc.core import ENV_LLM_LOGLEVEL

APPEND = "llm-append"

_logger = logging.getLogger(APPEND)

FILETYPE_PLAINTEXT = "plain-text"
FILETYPE_JSON = "json"
FILETYPE_JSONLINES = "jsonlines"
FILETYPE_CSV = "csv"
FILETYPE_TSV = "tsv"
FILETYPES = [
    FILETYPE_CSV,
    FILETYPE_JSON,
    FILETYPE_JSONLINES,
    FILETYPE_PLAINTEXT,
    FILETYPE_TSV,
]


def combine_text(input_files: List[str], output):
    """
    Combines text files line by line.

    :param input_files: the files to combine
    :type input_files: list
    :param output: the file pointer of the output
    """
    count = 0

    for input_file in input_files:
        _logger.info("Reading input file: %s" % input_file)
        with open(input_file, "r") as fp:
            for line in fp:
                count += 1
                output.write(line)
                if not line.endswith("\n") or line.endswith("\r"):
                    output.write("\n")
                # progress
                if (count % 1000) == 0:
                    _logger.info("%d lines processed" % count)

    _logger.info("%d lines processed in total" % count)


def combine_spreadsheet(input_files: List[str], file_type: str, output):
    """
    Combines CSV and TSV files.

    :param input_files: the files to combine
    :type input_files: list
    :param file_type: the file type
    :type file_type: str
    :param output: the file pointer of the output
    """
    fields = set()
    additional = []
    full_header = None

    # determine full header
    _logger.info("Determining header...")
    for input_file in input_files:
        _logger.info("Reading input file: %s" % input_file)
        with open(input_file, "r") as fp:
            if file_type == FILETYPE_CSV:
                reader = csv.DictReader(fp)
            else:
                reader = csv.DictReader(fp, delimiter="\t")
            row = next(reader)
            if full_header is None:
                full_header = list(row.keys())
                for f in row:
                    fields.add(f)
            else:
                for f in row:
                    if f not in fields:
                        fields.add(f)
                        full_header.append(f)
                        additional.append(f)
    if len(additional) > 0:
        _logger.warning("Subsequent files had additional column(s): %s" % ",".join(additional))

    # generate full output
    count = 0
    _logger.info("Generating output...")
    if file_type == FILETYPE_CSV:
        writer = csv.DictWriter(output, full_header)
    else:
        writer = csv.DictWriter(output, full_header, delimiter="\t")
    writer.writeheader()
    for input_file in input_files:
        _logger.info("Reading input file: %s" % input_file)
        with open(input_file, "r") as fp:
            if file_type == FILETYPE_CSV:
                reader = csv.DictReader(fp)
            else:
                reader = csv.DictReader(fp, delimiter="\t")
            for row in reader:
                count += 1
                writer.writerow(row)
                # progress
                if (count % 1000) == 0:
                    _logger.info("%d lines processed" % count)
    _logger.info("%d rows processed in total" % count)


def combine_json(input_files: List[str], output, pretty_print: bool):
    """
    Combines text files line by line.

    :param input_files: the files to combine
    :type input_files: list
    :param output: the file pointer of the output
    :param pretty_print: whether to output JSON pretty-printed
    :type pretty_print: bool
    """
    count = 0
    full_data = []
    fields = None
    additional = []

    for input_file in input_files:
        _logger.info("Reading input file: %s" % input_file)
        with open(input_file, "r") as fp:
            data = json.load(fp)
            if isinstance(data, dict):
                raise Exception("Input file is not an array: %s" % input_file)
            count += len(data)
            full_data.extend(data)
            if len(data) > 0:
                if isinstance(data[0], dict):
                    current = list(data[0].keys())
                    if fields is None:
                        fields = set(current)
                    else:
                        for f in current:
                            if f not in fields:
                                fields.add(f)
                                additional.append(f)
            _logger.info("%d records loaded" % len(data))

    if len(additional) > 0:
        _logger.warning("Subsequent files had additional field(s): %s" % ",".join(additional))

    if pretty_print:
        json.dump(full_data, output, indent=2)
    else:
        json.dump(full_data, output)
    _logger.info("%d records saved in total" % count)


def combine(input_files: List[str], file_type: str = FILETYPE_PLAINTEXT, output_file: str = None, pretty_print: bool = False):
    """
    Combines the input files by appending them.

    :param input_files: the files to append
    :type input_files: str
    :param file_type: the type of files to process
    :type file_type: str
    :param output_file: the file to store the result in, prints to stdout if None
    :type output_file: str
    :param pretty_print: whether to output JSON pretty-printed (does not apply to JSONLINES)
    :type pretty_print: bool
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
    if file_type in [FILETYPE_PLAINTEXT, FILETYPE_JSONLINES]:
        combine_text(input_files, output)
    elif (file_type == FILETYPE_CSV) or (file_type == FILETYPE_TSV):
        combine_spreadsheet(input_files, file_type, output)
    elif file_type == FILETYPE_JSON:
        combine_json(input_files, output, pretty_print)
    else:
        raise Exception("Unhandled file type: %s" % file_type)

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
        description="Tool for combining multiple text files by appending them.",
        prog=APPEND,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", type=str, help="Path to the text file(s) to append; glob syntax is supported", required=False, nargs="*")
    parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the data files to append", required=False, nargs="*")
    parser.add_argument("-t", "--file_type", choices=FILETYPES, help="The type of files that are being processed.", required=False, default=FILETYPE_PLAINTEXT)
    parser.add_argument("-o", "--output", metavar="FILE", help="The path of the file to store the combined data in; outputs it to stdout if omitted or a directory", default=None, type=str, required=False)
    parser.add_argument("-p", "--pretty_print", action="store_true", help="Whether to output the JSON in more human-readable format.", required=False)
    add_logging_level(parser)
    parsed = parser.parse_args(args=args)
    set_logging_level(_logger, parsed.logging_level)
    input_files = locate_files(parsed.input, input_lists=parsed.input_list, fail_if_empty=True)
    combine(input_files=input_files, file_type=parsed.file_type, output_file=parsed.output, pretty_print=parsed.pretty_print)


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
