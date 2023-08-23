# to-tsv-pretrain

* domain(s): pretrain
* accepts: PretrainData

Writes pretrain data in TSV format.

```
usage: to-tsv-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o OUTPUT
                       [--col_content COL]

Writes pretrain data in TSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the TSV file to write (directory when
                        processing multiple files) (default: None)
  --col_content COL     The name of the column for the content (default: None)
```
