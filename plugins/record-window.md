# record-window

* domain(s): pairs, pretrain, translation
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData

Only lets records pass that match the defined window and step size.

```
usage: record-window [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                     [-N LOGGER_NAME] [-f FROM_INDEX] [-t TO_INDEX] [-s STEP]

Only lets records pass that match the defined window and step size.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -f FROM_INDEX, --from_index FROM_INDEX
                        The 1-based lower bound of the window, ignored if not
                        supplied. (default: None)
  -t TO_INDEX, --to_index TO_INDEX
                        The 1-based upper bound of the window, ignored if not
                        supplied. (default: None)
  -s STEP, --step STEP  The increment to use (at least 1). (default: 1)
```
