# to-parquet-cl

* domain(s): classification
* accepts: ldc.api.supervised.classification.ClassificationData

Writes classification data in Parquet database format.

```
usage: to-parquet-cl [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                     [-N LOGGER_NAME] [--skip] -o OUTPUT [--col_text COL]
                     [--col_label COL] [--col_id COL]

Writes classification data in Parquet database format.

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
  --col_text COL        The name of the column for the text (default: None)
  --col_label COL       The name of the column for the label (default: None)
  --col_id COL          The name of the column for the row IDs (uses 'id' from
                        meta-data) (default: None)
```
