# to-csv-t9n

* domain(s): translation
* accepts: ldc.api.translation.TranslationData

Writes translation data in CSV format.

```
usage: to-csv-t9n [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                  [-N LOGGER_NAME] [--skip] -o OUTPUT -g LANG [LANG ...] [-n]
                  [--no_col_id] [--encoding ENC]

Writes translation data in CSV format.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -o OUTPUT, --output OUTPUT
                        Path of the CSV file to write (directory when
                        processing multiple files); Supported placeholders:
                        {HOME}, {CWD}, {TMP} (default: None)
  -g LANG [LANG ...], --languages LANG [LANG ...]
                        The language IDs (ISO 639-1) to output in separate
                        columns (default: None)
  -n, --no_header       For suppressing the header row (default: False)
  --no_col_id           For suppressing the column with the row IDs (default:
                        False)
  --encoding ENC        The encoding to force instead of using the default,
                        e.g., 'utf-8' (default: None)
```
