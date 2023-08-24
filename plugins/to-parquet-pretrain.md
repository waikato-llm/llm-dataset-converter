# to-parquet-pretrain

* domain(s): pretrain
* accepts: PretrainData

Writes text used for pretraining in Parquet database format.

```
usage: to-parquet-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o
                           OUTPUT [--col_content COL] [--col_id COL]

Writes text used for pretraining in Parquet database format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the CSV file to write (directory when
                        processing multiple files) (default: None)
  --col_content COL     The name of the column for the text content (default:
                        None)
  --col_id COL          The name of the column for the row IDs (uses 'id' from
                        meta-data) (default: None)
```
