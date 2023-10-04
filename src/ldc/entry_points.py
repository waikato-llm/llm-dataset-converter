import argparse
import sys
import traceback
from typing import List

from ldc.core import init_logging
from ldc.registry import ENTRY_POINT_DOWNLOADERS, ENTRY_POINT_READERS, ENTRY_POINT_FILTERS, ENTRY_POINT_WRITERS
from ldc.registry import register_plugins, available_downloaders, available_readers, available_filters, \
    available_writers
from seppl import generate_entry_points

ENTRY_POINTS = "llm-entry-points"


def output_entry_points(modules: List[str] = None):
    """
    Generates and outputs the entry points.

    :param modules: the modules to generate the entry points for
    :type modules: list
    """
    register_plugins(modules)

    # generate entry points
    entry_points = dict()
    entry_points[ENTRY_POINT_DOWNLOADERS] = list(available_downloaders().values())
    entry_points[ENTRY_POINT_READERS] = list(available_readers().values())
    entry_points[ENTRY_POINT_FILTERS] = list(available_filters().values())
    entry_points[ENTRY_POINT_WRITERS] = list(available_writers().values())

    print(generate_entry_points(entry_points))


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
