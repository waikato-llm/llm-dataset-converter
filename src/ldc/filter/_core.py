from typing import List

import seppl.io

from seppl.io import FILTER_ACTIONS, FILTER_ACTION_DISCARD, FILTER_ACTION_KEEP
from ldc.core import DomainHandler, DOMAIN_ANY


class Filter(seppl.io.Filter, DomainHandler):
    """
    Ancestor for ldc filters.
    """
    pass


class MultiFilter(seppl.io.MultiFilter, DomainHandler):

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_ANY]
