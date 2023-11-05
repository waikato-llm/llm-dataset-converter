import argparse
import logging
import sys
import traceback

from typing import List, Tuple, Optional, Dict

from seppl import enumerate_plugins, is_help_requested, split_args, args_to_objects
from ldc.core import init_logging, LOGGING_LEVELS, LOGGING_WARN, check_compatibility, CommandlineHandler, Session, set_logging_level
from ldc.help import generate_plugin_usage
from ldc.base_io import COMPRESSION_FORMATS, Reader, Writer
from ldc.execution import execute
from ldc.filter import Filter, MultiFilter
from ldc.registry import available_readers, available_filters, available_writers


CONVERT = "llm-convert"


def _available_plugins() -> Dict[str, CommandlineHandler]:
    """
    Returns the available reader/filter/writer plugins.

    :return: the dictionary of plugins (name/CommandlineHandler)
    :rtype: dict
    """
    result = dict()
    result.update(available_readers())
    result.update(available_filters())
    result.update(available_writers())
    return result


def _print_usage(plugin_details: bool = False):
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
        for plugin in sorted(_available_plugins().keys()):
            generate_plugin_usage(plugin)


def _parse_args(args: List[str], require_reader: bool = True, require_writer: bool = True) -> Tuple[Optional[Reader], Optional[Filter], Optional[Writer], Session]:
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
            _print_usage(plugin_details=plugin_details)
        sys.exit(0)

    parsed = split_args(args, list(_available_plugins().keys()))
    plugins = args_to_objects(parsed, _available_plugins(), allow_global_options=True)
    reader = None
    writer = None
    filters = []
    for plugin in plugins:
        if isinstance(plugin, Reader):
            if reader is None:
                reader = plugin
                continue
            else:
                raise Exception("Only one reader can be defined!")

        if isinstance(plugin, Filter):
            filters.append(plugin)
            continue

        if isinstance(plugin, Writer):
            if writer is None:
                writer = plugin
                continue
            else:
                raise Exception("Only one writer can be defined!")

        raise Exception("Unhandled plugin type: %s" % str(type(plugin)))

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
    if writer is not None:
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
    session.logger = logging.getLogger(CONVERT)
    set_logging_level(session.logger, session.options.logging_level)

    return reader, filter_, writer, session


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    init_logging()
    _args = sys.argv[1:] if (args is None) else args
    try:
        reader, filter_, writer, session = _parse_args(_args, require_writer=False)
    except Exception as e:
        traceback.print_exc()
        print("options: %s" % str(_args), file=sys.stderr)
        _print_usage()
        sys.exit(1)

    session.logger.info("options: %s" % str(_args))

    execute(reader, filter_, writer, session)


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
        return 1


if __name__ == '__main__':
    main()
