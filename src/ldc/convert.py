import argparse
import logging
import sys
import traceback

from typing import Tuple, Dict

from ldc import CommandlineHandler, Reader, Writer, StreamWriter, BatchWriter, Filter, MultiFilter
from ldc import is_help_requested, split_args, check_compatibility
from ldc.supervised.pairs import AlpacaReader, AlpacaWriter, Keyword


PROG = "llm-convert"

_logger = logging.getLogger(PROG)


def _add_to_dict(d: Dict[str, CommandlineHandler], h: CommandlineHandler):
    """
    Adds the plugin to the dictionary under its name.
    Raises an execption if plugin name already present.

    :param d: the dictionary to extend
    :type d: dict
    :param h: the plugin to add
    :type h: CommandlineHandler
    """
    if h.name() in d:
        raise Exception("Duplicate plugin name encountered: %s" % h.name())
    d[h.name()] = h


def available_readers() -> Dict[str, Reader]:
    """
    Returns all available readers.

    :return: the dict of reader objects
    :rtype: dict
    """
    result = dict()
    _add_to_dict(result, AlpacaReader())
    return result


def available_writers() -> Dict[str, Writer]:
    """
    Returns all available writers.

    :return: the dict of writer objects
    :rtype: dict
    """
    result = dict()
    _add_to_dict(result, AlpacaWriter())
    return result


def available_filters() -> Dict[str, Filter]:
    """
    Returns all available filters.

    :return: the dict of filter objects
    :rtype: dict
    """
    result = dict()
    _add_to_dict(result, Keyword())
    return result


def available_plugins() -> Dict[str, CommandlineHandler]:
    """
    Returns all available plugins.

    :return: the dict of plugin objects
    :rtype: dict
    """
    result = dict()
    result.update(available_readers())
    result.update(available_filters())
    result.update(available_writers())
    return result


def print_usage():
    """
    Prints the program usage to stdout.
    """
    cmd = "usage: " + PROG
    prefix = " " * len(cmd)
    print(cmd + " [-h] [-v]")
    print(prefix + "{%s}" % "|".join(available_readers().keys()))
    print(prefix + "[{%s}, ...]" % "|".join(available_filters().keys()))
    print(prefix + "{%s}" % "|".join(available_writers().keys()))
    print("\noptional arguments:")
    print("  -h, --help            show this help message and exit")
    print("  -v, --verbose         Whether to be more verbose with the output (default: False)")
    print()
    plugins = available_plugins()
    for k in sorted(plugins.keys()):
        header = k + " (" + "|".join(plugins[k].domains()) + ")"
        print("\n" + header + "\n" + "="*len(header))
        plugins[k].print_help()


def parse_args(args) -> Tuple[Reader, Filter, Writer, argparse.Namespace]:
    """
    Parses the arguments.

    :param args: the arguments to parse
    :type args: list
    :return: tuple of (reader, filter, writer, global_options), the filter can be None
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
    global_parser = argparse.ArgumentParser()
    global_parser.add_argument("-v", "--verbose", action="store_true")
    global_options = global_parser.parse_args(parsed[""] if ("" in parsed) else [])

    if global_options.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    return reader, filter_, writer, global_options


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    try:
        reader, filter_, writer, global_opts = parse_args(sys.argv[1:] if (args is None) else args)
    except Exception as e:
        print(e)
        print_usage()
        sys.exit(1)

    reader.initialize()
    if filter_ is not None:
        filter_.initialize()
    writer.initialize()

    try:
        count = 0
        if isinstance(writer, BatchWriter):
            data = []
            for item in reader.read():
                count += 1
                if (filter_ is None) or (filter_.keep(item)):
                    data.append(item)
                if global_opts.verbose and (count % 1000 == 0):
                    _logger.info("%d records processed..." % count)
            writer.write_batch(data)
        elif isinstance(writer, StreamWriter):
            for item in reader.read():
                count += 1
                if (filter_ is None) or filter_.keep(item):
                    writer.write_stream(item)
                if global_opts.verbose and (count % 1000 == 0):
                    _logger.info("%d records processed..." % count)
        else:
            raise Exception("Neither BatchWriter nor StreamWriter!")
    except:
        traceback.format_exc()

    reader.finalize()
    if filter_ is not None:
        filter_.finalize()
    writer.finalize()


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
        print(traceback.format_exc())
        return 1


if __name__ == '__main__':
    main()
