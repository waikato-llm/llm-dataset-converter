# to-alpaca

* domain(s): pairs
* accepts: ldc.api.supervised.pairs.PairData

Writes prompt/output pairs in Alpaca-like JSON format.

```
usage: to-alpaca [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                 [-N LOGGER_NAME] -o OUTPUT [-p] [-a]

Writes prompt/output pairs in Alpaca-like JSON format.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT, --output OUTPUT
                        Path of the Alpaca file to write (directory when
                        processing multiple files); Supported placeholders:
                        {HOME}, {CWD}, {TMP} (default: None)
  -p, --pretty_print    Whether to output the JSON in more human-readable
                        format. (default: False)
  -a, --ensure_ascii    Whether to ensure that the output is ASCII compatible.
                        (default: False)
```
