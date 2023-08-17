import logging
import sys
import traceback

from ldc.io import StreamWriter, BatchWriter
from ldc.args import print_usage, parse_args
from ldc.core import CONVERT, init_logging

_logger = logging.getLogger(CONVERT)


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    init_logging()
    try:
        reader, filter_, writer, session = parse_args(sys.argv[1:] if (args is None) else args)
    except Exception as e:
        print(e)
        print_usage()
        sys.exit(1)

    # propagate session
    reader.session = session
    if filter_ is not None:
        filter_.session = session
    writer.session = session

    # initialize
    reader.initialize()
    if filter_ is not None:
        filter_.initialize()
    writer.initialize()

    # process data
    try:
        while not reader.has_finished():
            if isinstance(writer, BatchWriter):
                data = []
                for item in reader.read():
                    session.count += 1
                    if filter_ is None:
                        data.append(item)
                    else:
                        item = filter_.process(item)
                        if item is not None:
                            data.append(item)
                    if session.count % 1000 == 0:
                        _logger.info("%d records processed..." % session.count)
                writer.write_batch(data)
                _logger.info("%d records processed in total." % session.count)
            elif isinstance(writer, StreamWriter):
                for item in reader.read():
                    session.count += 1
                    if filter_ is None:
                        writer.write_stream(item)
                    else:
                        item = filter_.process(item)
                        if item is not None:
                            writer.write_stream(item)
                    if session.count % 1000 == 0:
                        _logger.info("%d records processed..." % session.count)
                _logger.info("%d records processed in total." % session.count)
            else:
                raise Exception("Neither BatchWriter nor StreamWriter!")
    except:
        traceback.print_exc()

    # clean up
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
