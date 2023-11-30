# skip-duplicate-ids

* domain(s): pairs, pretrain, translation
* accepts: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData
* generates: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData

Suppresses records with IDs that have already passed through. Uses the 'id' value from the meta-data.

```
usage: skip-duplicate-ids [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                          [-N LOGGER_NAME]

Suppresses records with IDs that have already passed through. Uses the 'id'
value from the meta-data.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
```
