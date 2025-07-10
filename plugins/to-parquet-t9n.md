# to-parquet-t9n

* domain(s): translation
* accepts: ldc.api.translation.TranslationData

Writes translation data in Parquet database format. The translation data is output in JSON format: { "en": "Others have dismissed him as a joke.", "ro": "Alții l-au numit o glumă." }

```
usage: to-parquet-t9n [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                      [-N LOGGER_NAME] [--skip] -o OUTPUT [--col_content COL]
                      [--col_id COL]

Writes translation data in Parquet database format. The translation data is
output in JSON format: { "en": "Others have dismissed him as a joke.", "ro":
"Alții l-au numit o glumă." }

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
  --col_content COL     The name of the column for the translation data
                        (default: None)
  --col_id COL          The name of the column for the row IDs (uses 'id' from
                        meta-data) (default: None)
```
