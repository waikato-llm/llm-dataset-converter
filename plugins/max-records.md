# max-records

* domain(s): pairs, pretrain, translation
* accepts: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData
* generates: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData

Suppresses records after the specified maximum number of records have passed through.

```
usage: max-records [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-N LOGGER_NAME] [-m MAX_RECORDS]

Suppresses records after the specified maximum number of records have passed
through.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -m MAX_RECORDS, --max_records MAX_RECORDS
                        The maximum number number of records to let through
                        before suppressing records. (default: -1)
```
