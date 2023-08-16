# to-alpaca

* domain(s): pairs
* accepts: PairData

Writes prompt/output pairs in Alpaca-like JSON format.

```
usage: to-alpaca [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o OUTPUT

Writes prompt/output pairs in Alpaca-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the Alpaca file to write (directory when
                        processing multiple files) (default: None)
```
