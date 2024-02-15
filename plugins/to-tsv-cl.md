# to-tsv-cl

* domain(s): classification
* accepts: ldc.supervised.classification.ClassificationData

Writes classification data in TSV format.

```
usage: to-tsv-cl [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                 [-N LOGGER_NAME] -o OUTPUT [--col_text COL] [--col_label COL]
                 [--col_id COL] [-n]

Writes classification data in TSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT, --output OUTPUT
                        Path of the TSV file to write (directory when
                        processing multiple files) (default: None)
  --col_text COL        The name of the column for the text (default: None)
  --col_label COL       The name of the column for the labels (default: None)
  --col_id COL          The name of the column for the row IDs (uses 'id' from
                        meta-data) (default: None)
  -n, --no_header       For suppressing the header row (default: False)
```
