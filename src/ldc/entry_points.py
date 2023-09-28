import argparse
import importlib
import json
import sys
import traceback

from typing import List

from seppl import Plugin
from ldc.core import init_logging, CommandlineHandler
from ldc.registry import register_plugins, available_downloaders, available_readers, available_filters, available_writers
from ldc.registry import ENTRY_POINT_DOWNLOADERS, ENTRY_POINT_READERS, ENTRY_POINT_FILTERS, ENTRY_POINT_WRITERS

ENTRY_POINTS = "llm-entry-points"


def _to_entry_point(plugin: Plugin) -> str:
    """
    Turns the plugin into an entry point.

    :param plugin: the object to convert
    :type plugin: CommandlineHandler
    :return: the generated entry point
    :rtype: str
    """
    m = plugin.__module__

    # can we hide a private module?
    parts = m.split(".")
    if parts[-1].startswith("_"):
        parts.pop()
        m = ".".join(parts)
        try:
            importlib.import_module(m)
        except:
            # can't remove the last and private module, so we'll stick with the full path
            m = plugin.__module__

    result = plugin.name() + "=" + m + ":" + plugin.__class__.__name__
    return result


def _to_entry_points(plugins: List[Plugin]) -> List[str]:
    """
    Turns the plugins into a list of entry points.

    :param plugins: the plugins to convert
    :type plugins: list
    :return: the list of entry points
    :rtype: list
    """
    result = list()
    for plugin in plugins:
        result.append(_to_entry_point(plugin))
    return result


def output_entry_points(modules: List[str] = None):
    """
    Generates and outputs the entry points.

    :param modules: the modules to generate the entry points for
    :type modules: list
    """
    register_plugins(modules)

    # generate entry points
    entry_points = dict()
    entry_points[ENTRY_POINT_DOWNLOADERS] = _to_entry_points(list(available_downloaders().values()))
    entry_points[ENTRY_POINT_READERS] = _to_entry_points(list(available_readers().values()))
    entry_points[ENTRY_POINT_FILTERS] = _to_entry_points(list(available_filters().values()))
    entry_points[ENTRY_POINT_WRITERS] = _to_entry_points(list(available_writers().values()))
    keys = list(entry_points.keys())
    for k in keys:
        if len(entry_points[k]) == 0:
            entry_points.pop(k)

    # output
    print("entry_points=" + json.dumps(entry_points, indent=4))


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    init_logging()
    parser = argparse.ArgumentParser(
        description="Tool generating data for the 'entry_points' section in setup.py, populating it with the readers, filters and writers.",
        prog=ENTRY_POINTS,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--modules", metavar="PACKAGE", help="The names of the module packages, uses the default ones if not provided.", default=None, type=str, required=False, nargs="*")
    parsed = parser.parse_args(args=args)
    output_entry_points(parsed.modules)


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
