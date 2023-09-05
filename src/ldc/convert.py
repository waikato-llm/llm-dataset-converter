import sys
import traceback

from ldc.args import print_usage, parse_args
from ldc.core import init_logging
from ldc.execution import execute


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    init_logging()
    _args = sys.argv[1:] if (args is None) else args
    try:
        reader, filter_, writer, session = parse_args(_args)
    except Exception as e:
        print(e, file=sys.stderr)
        print("Arguments: %s" % str(_args), file=sys.stderr)
        print_usage()
        sys.exit(1)

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
