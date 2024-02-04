from typing import Optional, Dict


class MetaDataHandler(object):
    """
    Mixin for classes that manage meta-data.
    """

    def has_metadata(self) -> bool:
        """
        Returns whether meta-data is present.

        :return: True if meta-data present
        :rtype: bool
        """
        raise NotImplementedError()

    def get_metadata(self) -> Optional[Dict]:
        """
        Returns the meta-data.

        :return: the meta-data, None if not available
        :rtype: dict
        """
        raise NotImplementedError()

    def set_metadata(self, metadata: Optional[Dict]):
        """
        Sets the meta-data to use.

        :param metadata: the new meta-data, can be None
        :type metadata: dict
        """
        raise NotImplementedError()


def get_metadata(o) -> Optional[Dict]:
    """
    Retrieves the meta-data from the specified object.

    :param o: the object to get the meta-data from
    :return: the meta-data, None if not available
    """
    if isinstance(o, MetaDataHandler):
        return o.get_metadata()
    if hasattr(o, "meta"):
        obj = getattr(o, "meta")
        if isinstance(obj, dict):
            return obj
    return None


def add_metadata(meta: Optional[Dict], key: str, value) -> Dict:
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
