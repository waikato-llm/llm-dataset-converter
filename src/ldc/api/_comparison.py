import re
from typing import Tuple


COMPARISON_LESSTHAN = "lt"
COMPARISON_LESSOREQUAL = "le"
COMPARISON_EQUAL = "eq"
COMPARISON_NOTEQUAL = "ne"
COMPARISON_GREATEROREQUAL = "ge"
COMPARISON_GREATERTHAN = "gt"
COMPARISON_CONTAINS = "contains"
COMPARISON_MATCHES = "matches"

COMPARISONS = [
    COMPARISON_LESSTHAN,
    COMPARISON_LESSOREQUAL,
    COMPARISON_EQUAL,
    COMPARISON_NOTEQUAL,
    COMPARISON_GREATEROREQUAL,
    COMPARISON_GREATERTHAN,
]
COMPARISON_HELP = COMPARISON_LESSTHAN + ": less than, " \
    + COMPARISON_LESSOREQUAL + ": less or equal, " \
    + COMPARISON_EQUAL + ": equal, " \
    + COMPARISON_NOTEQUAL + ": not equal, " \
    + COMPARISON_GREATERTHAN + ": greater than, " \
    + COMPARISON_GREATEROREQUAL + ": greater of equal"

COMPARISONS_EXT = COMPARISONS[:]
COMPARISONS_EXT.append(COMPARISON_CONTAINS)
COMPARISONS_EXT.append(COMPARISON_MATCHES)
COMPARISON_EXT_HELP = COMPARISON_HELP + ", " \
                      + COMPARISON_CONTAINS + ": substring match, " \
                      + COMPARISON_MATCHES + ": regexp match"


def _ensure_same_type(v1, v2) -> Tuple:
    """
    Ensures that both values are of the same type.

    :param v1: the first value
    :param v2: the second value
    :return: the tuple of the updated values
    :rtype: tuple
    """
    if isinstance(v1, float):
        v2 = float(v2)
    elif isinstance(v1, int):
        v2 = int(v2)
    elif isinstance(v1, bool):
        v2 = str(v2).lower() == 'true'
    return v1, v2


def compare_values(v1, comparison: str, v2) -> bool:
    """
    Compares the two values using the specified comparison operator.

    :param v1: the first value
    :param comparison: the comparison to use (see COMPARISONS)
    :type comparison: str
    :param v2: the second value
    :return: the result of the comparison
    :rtype: bool
    """
    if comparison in [COMPARISON_CONTAINS, COMPARISON_MATCHES]:
        v1 = str(v1)
    else:
        v1, v2 = _ensure_same_type(v1, v2)

    # compare
    if comparison == COMPARISON_LESSTHAN:
        result = v1 < v2
    elif comparison == COMPARISON_LESSOREQUAL:
        result = v1 <= v2
    elif comparison == COMPARISON_EQUAL:
        result = v1 == v2
    elif comparison == COMPARISON_NOTEQUAL:
        result = v1 != v2
    elif comparison == COMPARISON_GREATERTHAN:
        result = v1 > v2
    elif comparison == COMPARISON_GREATEROREQUAL:
        result = v1 >= v2
    elif comparison == COMPARISON_CONTAINS:
        result = v2 in v1
    elif comparison == COMPARISON_MATCHES:
        result = re.search(v2, v1) is not None
    else:
        raise Exception("Unhandled comparison: %s" % comparison)
    return result
