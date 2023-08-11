from dataclasses import dataclass


@dataclass
class PairData:
    """
    Container for pair data.
    """
    instruction: str
    input: str
    output: str
    meta: dict

    @classmethod
    def parse(cls, d):
        """
        Obtains the data from the provided dictionary and creates a PairData instance.

        :param d: the dictionary to get the data from
        :type d: dict
        :return: the generated instance
        :rtype: PairData
        """
        return PairData(
            instruction=d.get("instruction", None),
            input=d.get("input", None),
            output=d.get("output", None),
            meta=None
        )
