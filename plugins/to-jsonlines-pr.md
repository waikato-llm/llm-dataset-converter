# to-jsonlines-pr

* domain(s): pairs
* accepts: ldc.supervised.pairs.PairData

Writes prompt/output pairs in JsonLines-like JSON format.

```
usage: to-jsonlines-pr [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                       [-N LOGGER_NAME] -o OUTPUT [--att_instruction ATT]
                       [--att_input ATT] [--att_output ATT] [--att_id ATT]
                       [-d NUM] [-b SIZE]

Writes prompt/output pairs in JsonLines-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT, --output OUTPUT
                        Path of the JsonLines file to write (directory when
                        processing multiple files) (default: None)
  --att_instruction ATT
                        The attribute for the instructions (default: None)
  --att_input ATT       The attribute for the inputs (default: None)
  --att_output ATT      The attribute for the outputs (default: None)
  --att_id ATT          The name of the attribute for the row IDs (uses 'id'
                        from meta-data) (default: None)
  -d NUM, --num_digits NUM
                        The number of digits to use for the filenames
                        (default: 6)
  -b SIZE, --buffer_size SIZE
                        The size of the record buffer when concatenating (to
                        improve I/O throughput) (default: 1000)
```
