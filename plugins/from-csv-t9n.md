# from-csv-t9n

* domain(s): translation
* generates: ldc.translation.TranslationData

Reads translation data in CSV format.

```
usage: from-csv-t9n [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                    [-N LOGGER_NAME] [-i [INPUT [INPUT ...]]]
                    [-I [INPUT_LIST [INPUT_LIST ...]]] -c COL [COL ...] -g
                    LANG [LANG ...] [-n] [--col_id COL]
                    [--col_meta [COL [COL ...]]] [--encoding ENC]

Reads translation data in CSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i [INPUT [INPUT ...]], --input [INPUT [INPUT ...]]
                        Path to the CSV file(s) to read; glob syntax is
                        supported (default: None)
  -I [INPUT_LIST [INPUT_LIST ...]], --input_list [INPUT_LIST [INPUT_LIST ...]]
                        Path to the text file(s) listing the data files to use
                        (default: None)
  -c COL [COL ...], --columns COL [COL ...]
                        The 1-based column indices with the language data
                        (default: None)
  -g LANG [LANG ...], --languages LANG [LANG ...]
                        The language IDs (ISO 639-1) corresponding to the
                        columns (default: None)
  -n, --no_header       For files with no header row (default: False)
  --col_id COL          The 1-based column containing the row ID (default:
                        None)
  --col_meta [COL [COL ...]]
                        The name (or 1-based index) of the columns to store in
                        the meta-data (default: None)
  --encoding ENC        The encoding to force instead of auto-detecting it,
                        e.g., 'utf-8' (default: None)
```
