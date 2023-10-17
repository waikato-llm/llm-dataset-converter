def str_to_column_index(c: str, fail_on_nondigit=False):
    """
    Attempts to turn the string column (name or 1-based column index)
    into a 0-based integer index.

    :param c: the column name/index to process
    :type c: str
    :param fail_on_nondigit: raises an exception if not a numeric index
    :type fail_on_nondigit: bool
    :return: the index or -1 if not an index
    :rtype: int
    """
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
