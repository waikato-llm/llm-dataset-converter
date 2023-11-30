# split-pt

* domain(s): pretrain
* accepts: ldc.pretrain.PretrainData
* generates: ldc.pretrain.PretrainData

Splits pretrain text data into separate records on new lines. Automatically skips empty lines.

```
usage: split-pt [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-N LOGGER_NAME]

Splits pretrain text data into separate records on new lines. Automatically
skips empty lines.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
```
