import logging
import sys
import traceback

from ldc.io import StreamWriter, BatchWriter
from ldc.args import print_usage, parse_args, PROG

_logger = logging.getLogger(PROG)


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
