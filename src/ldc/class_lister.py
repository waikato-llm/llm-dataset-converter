from typing import List, Dict


def list_classes() -> Dict[str, List[str]]:
    return {
        "ldc.api.Downloader": [
            "ldc.downloader",
        ],
        "ldc.api.Reader": [
            "ldc.pretrain",
            "ldc.supervised.classification",
            "ldc.supervised.pairs",
            "ldc.translation",
        ],
        "ldc.api.Filter": [
            "ldc.filter",
            "ldc.pretrain",
            "ldc.supervised.classification",
            "ldc.supervised.pairs",
            "ldc.translation",
        ],
        "seppl.io.Writer": [
            "ldc.pretrain",
            "ldc.supervised.classification",
            "ldc.supervised.pairs",
            "ldc.translation",
        ],
    }
