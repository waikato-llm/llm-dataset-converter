import argparse
import os
import sys
from typing import List, Dict, Tuple, Iterable, Optional

from ldc.core import OutputProducer, InputConsumer, DomainHandler, check_compatibility, classes_to_str, Session, CONVERT
from ldc.core import LOGGING_LEVELS, LOGGING_WARN, set_logging_level
from ldc.io import Reader, Writer, COMPRESSION_FORMATS
from ldc.filter import Filter, MultiFilter
from ldc.registry import available_readers, available_filters, available_writers, available_plugins


HELP_FORMAT_TEXT = "text"
HELP_FORMAT_MARKDOWN = "markdown"
HELP_FORMATS = [
    HELP_FORMAT_TEXT,
    HELP_FORMAT_MARKDOWN,
]


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


def is_help_requested(args: List[str]) -> Tuple[bool, bool, str]:
    """
    Checks whether help was requested.

    :param args: the arguments to check
    :type args: list
    :return: the tuple of help requested: (help_requested, plugin_details, plugin_name)
    :rtype: tuple
    """
    help_requested = False
    plugin_details = False
    plugin_name = None
    for index, arg in enumerate(args):
        if (arg == "-h") or (arg == "--help"):
            help_requested = True
            break
        if arg == "--help-all":
            help_requested = True
            plugin_details = True
            break
        if arg == "--help-plugin":
            help_requested = True
            if index < len(args) - 1:
                plugin_name = args[index + 1]
            break
    return help_requested, plugin_details, plugin_name


def enumerate_plugins(plugins: Iterable[str], prefix: str = "", width: int = 72) -> str:
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
    for plugin in sorted(plugins):
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


def generate_plugin_usage(plugin_name: str, help_format: str = HELP_FORMAT_TEXT, heading_level: int = 1,
                          output_path: str = None):
    """
    Generates the usage help screen for the specified plugin.

    :param plugin_name: the plugin to generate the usage for (name used on command-line)
    :type plugin_name: str
    :param help_format: the format to use for the output
    :type help_format: str
    :param heading_level: the level to use for the heading (markdown)
    :type heading_level: int
    :param output_path: the directory (automatically generates output name from plugin name and output format) or file to store the generated help in, uses stdout if None
    :type output_path: str
    """
    if help_format not in HELP_FORMATS:
        raise Exception("Unhandled help format: %s" % help_format)

    plugin = available_plugins()[plugin_name]

    result = ""
    if help_format == HELP_FORMAT_TEXT:
        suffix = ".txt"
        result += "\n" + plugin_name + "\n" + "=" * len(plugin_name) + "\n"
        if isinstance(plugin, DomainHandler):
            result += "domain(s): " + ", ".join(plugin.domains()) + "\n"
        if isinstance(plugin, InputConsumer):
            result += "accepts: " + classes_to_str(plugin.accepts()) + "\n"
        if isinstance(plugin, OutputProducer):
            result += "generates: " + classes_to_str(plugin.generates()) + "\n"
        result += "\n"
        result += plugin.format_help() + "\n"
    elif help_format == HELP_FORMAT_MARKDOWN:
        suffix = ".md"
        result += "#"*heading_level + " " + plugin_name + "\n"
        result += "\n"
        if isinstance(plugin, DomainHandler):
            result += "* domain(s): " + ", ".join(plugin.domains()) + "\n"
        if isinstance(plugin, InputConsumer):
            result += "* accepts: " + classes_to_str(plugin.accepts()) + "\n"
        if isinstance(plugin, OutputProducer):
            result += "* generates: " + classes_to_str(plugin.generates()) + "\n"
        result += "\n"
        result += plugin.description() + "\n"
        result += "\n"
        result += "```\n"
        result += plugin.format_help()
        result += "```\n"
    else:
        raise Exception("Unhandled help format: %s" % help_format)

    if output_path is None:
        print(result)
    else:
        if os.path.isdir(output_path):
            output_file = os.path.join(output_path, plugin.name() + suffix)
        else:
            output_file = output_path
        with open(output_file, "w") as fp:
            fp.write(result)


def print_usage(plugin_details: bool = False):
    """
    Prints the program usage to stdout.
    Ensure global options are in sync with parser in parse_args method below.

    :param plugin_details: whether to output the plugin details as well
    :type plugin_details: bool
    """
    cmd = "usage: " + CONVERT
    prefix = " " * (len(cmd) + 1)
    compression_formats = "None," + ",".join(COMPRESSION_FORMATS)
    logging_levels = ",".join(LOGGING_LEVELS)
    print(cmd + " [-h|--help|--help-all|-help-plugin NAME]")
    print(prefix + "[-c {%s}]" % compression_formats)
    print(prefix + "[-l {%s}]" % logging_levels)
    print(prefix + "reader")
    print(prefix + "[filter [filter [...]]]")
    print(prefix + "writer")
    print()
    print("Tool for converting between large language model (LLM) dataset formats.")
    print()
    print("readers:\n" + enumerate_plugins(available_readers().keys(), prefix="   "))
    print("filters:\n" + enumerate_plugins(available_filters().keys(), prefix="   "))
    print("writers:\n" + enumerate_plugins(available_writers().keys(), prefix="   "))
    print()
    print("optional arguments:")
    print("  -h, --help            show basic help message and exit")
    print("  --help-all            show basic help message plus help on all plugins and exit")
    print("  --help-plugin NAME    show help message for plugin NAME and exit")
    print("  -l {%s}, --logging_level {%s}" % (logging_levels, logging_levels))
    print("                        the logging level to use (default: WARN)")
    print("  -c {%s}, --compression {%s}" % (compression_formats, compression_formats))
    print("                        the type of compression to use when only providing an output")
    print("                        directory to the writer (default: None)")
    print()
    if plugin_details:
        plugins = available_plugins()
        for k in sorted(plugins.keys()):
            generate_plugin_usage(k)


def parse_args(args: List[str], require_reader: bool = True, require_writer: bool = True) -> Tuple[Optional[Reader], Optional[Filter], Optional[Writer], Session]:
    """
    Parses the arguments.

    :param args: the arguments to parse
    :type args: list
    :param require_reader: whether a reader is required
    :type require_reader: bool
    :param require_writer: whether a writer is required
    :type require_writer: bool
    :return: tuple of (reader, filter, writer, session), the filter can be None
    :rtype: tuple
    """
    # help requested?
    help_requested, plugin_details, plugin_name = is_help_requested(args)
    if help_requested:
        if plugin_name is not None:
            generate_plugin_usage(plugin_name)
        else:
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
    if (reader is None) and require_reader:
        raise Exception("No reader defined!")
    if (writer is None) and require_writer:
        raise Exception("No writer defined!")
    if len(filters) == 0:
        filter_ = None
    elif len(filters) == 1:
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
    parser.add_argument("-l", "--logging_level", choices=LOGGING_LEVELS, default=LOGGING_WARN)
    parser.add_argument("-c", "--compression", default=None, choices=COMPRESSION_FORMATS)
    session = Session(options=parser.parse_args(parsed[""] if ("" in parsed) else []))
    set_logging_level(session.logger, session.options.logging_level)

    return reader, filter_, writer, session
