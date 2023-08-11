import json

from ._data import PairData


def load_alpaca(fp):
    """
    Loads the data in alpaca format and returns the items one by one.

    :param fp: the file like object to read the JSON from
    :type fp: file
    :return: the data
    :rtype: PairData
    """
    array = json.load(fp)
    for item in array:
        yield PairData.parse(item)
