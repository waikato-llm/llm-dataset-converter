from typing import Dict, Optional


def str_to_column_index(c: str, fail_on_nondigit=False):
    """
    Attempts to turn the string column (name or 1-based column index)
    into a 0-based integer index.

    :param c: the column name/index to process, can be None
    :type c: str
    :param fail_on_nondigit: raises an exception if not a numeric index
    :type fail_on_nondigit: bool
    :return: the index or -1 if not an index
    :rtype: int
    """
    if c is None:
        if fail_on_nondigit:
            raise Exception("Failed to parse column: %s" % c)
        else:
            return -1
    if c.isdigit():
        try:
            return int(c) - 1
        except:
            if fail_on_nondigit:
                raise Exception("Failed to parse column: %s" % c)
            else:
                return -1
    else:
        if fail_on_nondigit:
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
