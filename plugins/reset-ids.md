# reset-ids

* domain(s): pairs, pretrain, translation
* accepts: PairData, PretrainData, TranslationData
* generates: PairData, PretrainData, TranslationData

Resets the IDs in the meta-data using consecutive integer ones.

```
usage: reset-ids [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-o OFFSET]

Resets the IDs in the meta-data using consecutive integer ones.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OFFSET, --offset OFFSET
                        The offset for the ID counter (default: 0)
```
