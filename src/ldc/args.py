import argparse
import logging
import sys
from typing import List, Dict, Tuple, Iterable

from ldc.core import OutputProducer, InputConsumer, check_compatibility, classes_to_str, Session, CONVERT
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


def is_help_requested(args: List[str]) -> Tuple[bool, bool]:
    """
    Checks whether help was requested.

    :param args: the arguments to check
    :type args: list
    :return: the tuple of help requested: (help_requested, plugin_details)
    :rtype: tuple
    """
    help_requested = False
    plugin_details = False
    for arg in args:
        if (arg == "-h") or (arg == "--help"):
            help_requested = True
            break
        if arg == "--help-all":
            help_requested = True
            plugin_details = True
            break
    return help_requested, plugin_details


def _enumerate_plugins(plugins: Iterable[str], prefix: str = "", width: int = 72) -> str:
    """
    Turns the list of plugin names into a string.

    :param plugins: the plugin names to turn into a string
    :type plugins: Iterable
    :param prefix: the prefix string to use for each line
    :type prefix: str
    :param width: the maximum width of the string before adding a newline
    :type width: int
    :return: the generated string
    :rtype: str
    """
    result = []
    line = prefix
    for plugin in plugins:
        if (len(line) > 0) and (line[-1] != " "):
            line += ", "
        if len(line) + len(plugin) >= width:
            result.append(line)
            line = prefix + plugin
        else:
            line += plugin
    if len(line) > 0:
        result.append(line)
    return "\n".join(result)


def print_plugin_usage(plugin_name: str):
    """
    Outputs the usage for the specified plugin.

    :param plugin_name: the plugin to output the usage for (name used on command-line)
    :type plugin_name: str
    """
    plugin = available_plugins()[plugin_name]
    print("\n" + plugin_name + "\n" + "=" * len(plugin_name))
    print("domain(s): " + ", ".join(plugin.domains()))
    if isinstance(plugin, InputConsumer):
        print("accepts: " + classes_to_str(plugin.accepts()))
    if isinstance(plugin, OutputProducer):
        print("generates: " + classes_to_str(plugin.generates()))
    print()
    plugin.print_help()


def print_usage(plugin_details: bool = False):
    """
    Prints the program usage to stdout.
    Ensure global options are in sync with parser in parse_args method below.

    :param plugin_details: whether to output the plugin details as well
    :type plugin_details: bool
    :param plugin: the plugin to limit the help to
    :type plugin: str
    """
    cmd = "usage: " + CONVERT
    prefix = " " * (len(cmd) + 1)
    print(cmd + " [-h|--help|--help-all] [-v]")
    print(prefix + "reader")
    print(prefix + "[filter [filter [...]]]")
    print(prefix + "writer")
    print()
    print("Tool for converting between large language model (LLM) dataset formats.")
    print()
    print("readers:\n" + _enumerate_plugins(available_readers().keys(), prefix="   "))
    print("filters:\n" + _enumerate_plugins(available_filters().keys(), prefix="   "))
    print("writers:\n" + _enumerate_plugins(available_writers().keys(), prefix="   "))
    print()
    print("optional arguments:")
    print("  -h, --help            show basic help message and exit")
    print("  --help-all            show basic help message plus help on all plugins and exit")
    print("  -v, --verbose         Whether to be more verbose with the output (default: False)")
    print()
    if plugin_details:
        plugins = available_plugins()
        for k in sorted(plugins.keys()):
            print_plugin_usage(k)


def parse_args(args: List[str]) -> Tuple[Reader, Filter, Writer, Session]:
    """
    Parses the arguments.

    :param args: the arguments to parse
    :type args: list
    :return: tuple of (reader, filter, writer, session), the filter can be None
    :rtype: tuple
    """
    # help requested?
    help_requested, plugin_details = is_help_requested(args)
    if help_requested:
        print_usage(plugin_details=plugin_details)
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
