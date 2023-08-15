import argparse
import logging
import sys
from typing import List, Dict, Tuple

from ldc.core import OutputProducer, InputConsumer, check_compatibility, classes_to_str, Session, PROG
from ldc.io import Reader, Writer
from ldc.filter import Filter, MultiFilter
from ldc.registry import available_readers, available_filters, available_writers, available_plugins


def split_args(args: List[str], handlers: List[str]) -> Dict[str, List[str]]:
    """
    Splits the command-line arguments into handler and their associated arguments.
    Special entry "" is used for global options.

    :param args: the command-line arguments to split
    :type args: list
    :param handlers: the list of valid handler names
    :type handlers: list
    :return: the dictionary for handler name / options list
    :rtype: dict
    """
    handlers = set(handlers)
    result = dict()
    last_handler = ""
    last_args = []

    for arg in args:
        if arg in handlers:
            result[last_handler] = last_args
            last_handler = arg
            last_args = []
            continue
        else:
            last_args.append(arg)

    if last_handler is not None:
        result[last_handler] = last_args

    return result


def is_help_requested(args: List[str]):
    """
    Checks whether help was requested.

    :param args: the arguments to check
    :type args: list
    :return: True if help requested
    :rtype: bool
    """
    result = False
    for arg in args:
        if (arg == "-h") or (arg == "--help"):
            result = True
            break
    return result


def print_usage():
    """
    Prints the program usage to stdout.
    Ensure global options are in sync with parser in parse_args method below.
    """
    cmd = "usage: " + PROG
    prefix = " " * (len(cmd) + 1)
    print(cmd + " [-h] [-v]")
    print(prefix + "{%s}" % "|".join(available_readers().keys()))
    print(prefix + "[%s, ...]" % "|".join(available_filters().keys()))
    print(prefix + "{%s}" % "|".join(available_writers().keys()))
    print("\noptional arguments:")
    print("  -h, --help            show this help message and exit")
    print("  -v, --verbose         Whether to be more verbose with the output (default: False)")
    print()
    plugins = available_plugins()
    for k in sorted(plugins.keys()):
        plugin = plugins[k]
        print("\n" + k + "\n" + "="*len(k))
        print("domain(s): " + ", ".join(plugin.domains()))
        if isinstance(plugin, OutputProducer):
            print("generates: " + classes_to_str(plugin.generates()))
        if isinstance(plugin, InputConsumer):
            print("accepts: " + classes_to_str(plugin.accepts()))
        print()
        plugin.print_help()


def parse_args(args: List[str]) -> Tuple[Reader, Filter, Writer, Session]:
    """
    Parses the arguments.

    :param args: the arguments to parse
    :type args: list
    :return: tuple of (reader, filter, writer, session), the filter can be None
    :rtype: tuple
    """
    # help requested?
    if is_help_requested(args):
        print_usage()
        sys.exit(0)

    parsed = split_args(args, list(available_plugins().keys()))
    all_readers = available_readers()
    all_writers = available_writers()
    all_filters = available_filters()
    reader = None
    writer = None
    filters = []
    for arg in parsed:
        if arg in all_readers:
            if reader is None:
                reader = all_readers[arg]
                reader.parse_args(parsed[arg])
            else:
                raise Exception("Only one reader can be defined!")
            continue
        if arg in all_writers:
            if writer is None:
                writer = all_writers[arg]
                writer.parse_args(parsed[arg])
            else:
                raise Exception("Only one writer can be defined!")
            continue
        if arg in all_filters:
            f = all_filters[arg]
            f.parse_args(parsed[arg])
            filters.append(f)

    # checks whether valid pipeline
    if reader is None:
        raise Exception("No reader defined!")
    if writer is None:
        raise Exception("No writer defined!")
    if len(filters) == 0:
        filter_ = None
    elif len(filters) == 0:
        filter_ = filters[0]
    else:
        filter_ = MultiFilter(filters=filters)

    # check domain compatibility
    if filter_ is not None:
        check_compatibility([reader, filter_, writer])
    else:
        check_compatibility([reader, writer])

    # global options?
    # see print_usage() method above
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    session = Session(options=parser.parse_args(parsed[""] if ("" in parsed) else []))
    logging.basicConfig(level=logging.WARNING)
    if session.options.verbose:
        session.logger.setLevel(logging.INFO)

    return reader, filter_, writer, session
