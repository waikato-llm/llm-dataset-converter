# to-parquet-pt

* domain(s): pretrain
* accepts: ldc.api.pretrain.PretrainData

Writes text used for pretraining in Parquet database format.

```
usage: to-parquet-pt [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                     [-N LOGGER_NAME] -o OUTPUT [--col_content COL]
                     [--col_id COL]

Writes text used for pretraining in Parquet database format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT, --output OUTPUT
                        Path of the CSV file to write (directory when
                        processing multiple files) (default: None)
  --col_content COL     The name of the column for the text content (default:
                        None)
  --col_id COL          The name of the column for the row IDs (uses 'id' from
                        meta-data) (default: None)
```
