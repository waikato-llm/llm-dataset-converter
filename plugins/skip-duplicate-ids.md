# skip-duplicate-ids

* domain(s): pairs, pretrain, translation
* accepts: PairData, PretrainData, TranslationData
* generates: PairData, PretrainData, TranslationData

Suppresses records with IDs that have already passed through. Uses the 'id' value from the meta-data.

```
usage: skip-duplicate-ids [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]

Suppresses records with IDs that have already passed through. Uses the 'id'
value from the meta-data.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
```
