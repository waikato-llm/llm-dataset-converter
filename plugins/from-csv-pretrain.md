# from-csv-pretrain

* domain(s): pretrain
* generates: PretrainData

Reads pretrain data in CSV format.

```
usage: from-csv-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i INPUT
                         [INPUT ...] [--col_content COL]

Reads pretrain data in CSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the CSV file(s) to read; glob syntax is
                        supported (default: None)
  --col_content COL     The name of the column with the text content (default:
                        None)
```
