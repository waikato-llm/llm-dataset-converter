import numpy as np

from typing import Dict, Optional, List


class Splitter:
    """
    Class for dividing a token stream into sub-streams.
    """

    def __init__(self, split_ratios: List[int], split_names: List[str]):
        """
        Initializes the splitter.

        :param split_ratios: the list of (int) ratios to use (must sum up to 100)
        :type split_ratios: list
        :param split_names: the list of names to use for the splits
        :type split_names: list
        """
        self.split_ratios = split_ratios
        self.split_names = split_names
        self._schedule = None
        self._counter = 0
        self._stats = None

    def initialize(self):
        """
        Initializes the splitter, throws exceptions if undefined state or incorrect values.
        """
        if self.split_ratios is None:
            raise Exception("No split ratios defined!")
        if self.split_names is None:
            raise Exception("No split name defined!")
        if len(self.split_ratios) != len(self.split_names):
            raise Exception("Differing number of split ratios and names: %d != %d" % (len(self.split_ratios), len(self.split_names)))
        if sum(self.split_ratios) != 100:
            raise Exception("Split ratios must sum up to 100, but got: %d" % sum(self.split_ratios))

        # compute greatest common denominator and generate schedule
        gcd = np.gcd.reduce(np.asarray(self.split_ratios))
        self._schedule = [0] * (len(self.split_ratios) + 1)
        for i, ratio in enumerate(self.split_ratios):
            self._schedule[i + 1] = self._schedule[i] + ratio / gcd
        self._counter = 0
        self._stats = dict()

    def reset(self):
        """
        Resets the counter and stats.
        """
        self._counter = 0
        self._stats = dict()

    def next(self) -> str:
        """
        Returns the next split name.

        :return: the name of the split
        :rtype: str
        """
        split = None
        for i in range(len(self.split_names)):
            if (self._counter >= self._schedule[i]) and (self._counter < self._schedule[i + 1]):
                split = self.split_names[i]

        # update counter
        self._counter += 1
        if self._counter == self._schedule[-1]:
            self._counter = 0

        # update stats
        if split not in self._stats:
            self._stats[split] = 0
        self._stats[split] += 1

        return split

    def stats(self) -> Dict:
        """
        Returns the statistics.
        """
        return self._stats

    def counter(self) -> int:
        """
        Returns the counter.
        """
        return self._counter


def str_to_column_index(c: str, fail_on_non_digit=False):
    """
    Attempts to turn the string column (name or 1-based column index)
    into a 0-based integer index.

    :param c: the column name/index to process, can be None
    :type c: str
    :param fail_on_non_digit: raises an exception if not a numeric index
    :type fail_on_non_digit: bool
    :return: the index or -1 if not an index
    :rtype: int
    """
    if c is None:
        if fail_on_non_digit:
            raise Exception("Failed to parse column: %s" % c)
        else:
            return -1
    if c.isdigit():
        try:
            return int(c) - 1
        except:
            if fail_on_non_digit:
                raise Exception("Failed to parse column: %s" % c)
            else:
                return -1
    else:
        if fail_on_non_digit:
            raise Exception("Failed to parse column: %s" % c)
        else:
            return -1


def add_meta_data(meta: Optional[Dict], key: str, value) -> Dict:
    """
    Adds the specified key/value pair to the meta-data.
    If the provided meta-data dictionary is empty, it gets instantiated.
    If value is None, nothing gets added.
    If value is a string and empty, nothing gets added.

    :param meta: the meta-data to add to
    :type meta: dict
    :param key: the key to store the value under
    :type key: str
    :param value: the value to store
    :return: the created or updated dictionary
    :rtype: dict
    """
    if value is None:
        return meta
    if isinstance(value, str) and (len(value) == 0):
        return meta
    if meta is None:
        meta = dict()
    meta[key] = value
    return meta
