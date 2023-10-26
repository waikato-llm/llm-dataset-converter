import sys
import traceback

from typing import List

from seppl import enumerate_plugins, is_help_requested, split_args, args_to_objects
from ldc.core import init_logging
from ldc.downloader import Downloader
from ldc.help import generate_plugin_usage
from ldc.registry import available_downloaders


DOWNLOAD = "llm-download"


def _print_usage(plugin_details: bool = False):
    """
    Prints the program usage to stdout.
    Ensure global options are in sync with parser in parse_args method below.

    :param plugin_details: whether to output the plugin details as well
    :type plugin_details: bool
    """
    cmd = "usage: " + DOWNLOAD
    prefix = " " * (len(cmd) + 1)
    print(cmd + " [-h|--help|--help-all|-help-plugin NAME]")
    print(prefix + "downloader")
    print()
    print("Tool for downloading data for large language models (LLMs).")
    print()
    print("downloaders:\n" + enumerate_plugins(available_downloaders().keys(), prefix="   "))
    print()
    print("optional arguments:")
    print("  -h, --help            show basic help message and exit")
    print("  --help-all            show basic help message plus help on all plugins and exit")
    print("  --help-plugin NAME    show help message for plugin NAME and exit")
    print()
    if plugin_details:
        for plugin in sorted(available_downloaders().keys()):
            generate_plugin_usage(plugin)


def _parse_args(args: List[str]) -> Downloader:
    """
    Parses the arguments.

    :param args: the arguments to parse
    :type args: list
    :return: the downloader
    :rtype: Downloader
    """
    # help requested?
    help_requested, plugin_details, plugin_name = is_help_requested(args)
    if help_requested:
        if plugin_name is not None:
            generate_plugin_usage(plugin_name)
        else:
            _print_usage(plugin_details=plugin_details)
        sys.exit(0)

    args = split_args(args, list(available_downloaders().keys()))
    downloaders = args_to_objects(args, available_downloaders(), allow_global_options=False)
    if len(downloaders) == 0:
        raise Exception("No downloader defined!")
    elif len(downloaders) > 1:
        raise Exception("Only one downloader can be defined!")
    else:
        return downloaders[0]


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    init_logging()
    _args = sys.argv[1:] if (args is None) else args
    try:
        downloader = _parse_args(_args)
    except Exception as e:
        print(e, file=sys.stderr)
        print("options: %s" % str(_args), file=sys.stderr)
        _print_usage()
        sys.exit(1)

    downloader.logger().info("options: %s" % str(_args))
    downloader.initialize()
    downloader.download()
    downloader.finalize()


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
