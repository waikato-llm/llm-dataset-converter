import logging
import traceback

from typing import Union, List, Optional

from ldc.io import Reader, Writer, StreamWriter, BatchWriter, Session
from ldc.filter import Filter, MultiFilter


def execute(reader: Reader, filters: Optional[Union[Filter, List[Filter]]], writer: Writer,
            session: Session, _logger: logging.Logger):
    """
    Executes the pipeline.

    :param reader: the reader to use
    :type reader: Reader
    :param filters: the filter(s) to use, can be None
    :type filters: list or Filter
    :param writer: the writer to use
    :type writer: Writer
    :param session: the session object to use
    :type session: Session
    :param _logger: the logging instance to use
    :type _logger: logging.Logger
    """
    # assemble filter
    if isinstance(filters, Filter):
        filter_ = filters
    elif isinstance(filters, list):
        filter_ = MultiFilter(filters=filters)
    elif filters is None:
        filter_ = None
    else:
        raise Exception("Unhandled filter(s) type: %s" % str(type(filters)))

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
