# from-alpaca

* domain(s): pairs
* generates: PairData

Reads prompt/output pairs in Alpaca-like JSON format.

```
usage: from-alpaca [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-N LOGGER_NAME]
                   -i INPUT [INPUT ...]

Reads prompt/output pairs in Alpaca-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the Alpaca file(s) to read; glob syntax is
                        supported (default: None)
```
