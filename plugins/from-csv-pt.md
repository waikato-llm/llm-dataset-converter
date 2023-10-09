# from-csv-pt

* domain(s): pretrain
* generates: ldc.pretrain.PretrainData

Reads pretrain data in CSV format.

```
usage: from-csv-pt [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-N LOGGER_NAME]
                   -i INPUT [INPUT ...] [-c COL] [--col_id COL] [-n]

Reads pretrain data in CSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the CSV file(s) to read; glob syntax is
                        supported (default: None)
  -c COL, --col_content COL
                        The name (or 1-based index if no header row) of the
                        column with the text content (default: None)
  --col_id COL          The name (or 1-based index if no header row) of the
                        column with the row IDs (gets stored under 'id' in
                        meta-data) (default: None)
  -n, --no_header       For files with no header row (default: False)
```
