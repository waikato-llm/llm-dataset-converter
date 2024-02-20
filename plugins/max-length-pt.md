# max-length-pt

* domain(s): pretrain
* accepts: ldc.api.pretrain.PretrainData
* generates: ldc.api.pretrain.PretrainData

Splits pretrain text into segments of at most the specified length (uses word boundary).

```
usage: max-length-pt [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                     [-N LOGGER_NAME] [-m MAX_LENGTH] [-s]

Splits pretrain text into segments of at most the specified length (uses word
boundary).

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -m MAX_LENGTH, --max_length MAX_LENGTH
                        The maximum text length, use <=0 for unbounded.
                        (default: -1)
  -s, --split_records   Splits the lines into separate records (one line per
                        record) after reassambling the lines instead of
                        combining them back into single document. (default:
                        False)
```
