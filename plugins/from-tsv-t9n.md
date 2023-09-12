# from-tsv-t9n

* domain(s): translation
* generates: TranslationData

Reads translation data in TSV format.

```
usage: from-tsv-t9n [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                    [-N LOGGER_NAME] -i INPUT [INPUT ...] -c COL [COL ...] -g
                    LANG [LANG ...] [-n] [--col_id COL]

Reads translation data in TSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the TSV file(s) to read; glob syntax is
                        supported (default: None)
  -c COL [COL ...], --columns COL [COL ...]
                        The 1-based column indices with the language data
                        (default: None)
  -g LANG [LANG ...], --languages LANG [LANG ...]
                        The language IDs (ISO 639-1) corresponding to the
                        columns (default: None)
  -n, --no_header       For files with no header row (default: False)
  --col_id COL          The 1-based column containing the row ID (default:
                        None)
```
