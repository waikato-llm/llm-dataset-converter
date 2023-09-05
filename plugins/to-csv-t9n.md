# to-csv-t9n

* domain(s): translation
* accepts: TranslationData

Writes translation data in CSV format.

```
usage: to-csv-t9n [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o OUTPUT -g LANG
                  [LANG ...] [-n] [--no_col_id]

Writes translation data in CSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the CSV file to write (directory when
                        processing multiple files) (default: None)
  -g LANG [LANG ...], --languages LANG [LANG ...]
                        The language IDs (ISO 639-1) to output in separate
                        columns (default: None)
  -n, --no_header       For suppressing the header row (default: False)
  --no_col_id           For suppressing the column with the row IDs (default:
                        False)
```
