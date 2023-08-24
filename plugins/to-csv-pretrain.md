# to-csv-pretrain

* domain(s): pretrain
* accepts: PretrainData

Writes pretrain data in CSV format.

```
usage: to-csv-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o OUTPUT
                       [-c COL] [--col_id COL] [-n]

Writes pretrain data in CSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the CSV file to write (directory when
                        processing multiple files) (default: None)
  -c COL, --col_content COL
                        The name of the column for the content when outputting
                        a header row (default: None)
  --col_id COL          The name of the column for the row IDs (uses 'id' from
                        meta-data) (default: None)
  -n, --no_header       For suppressing the header row (default: False)
```
