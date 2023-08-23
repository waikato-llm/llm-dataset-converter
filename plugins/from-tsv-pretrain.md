# from-tsv-pretrain

* domain(s): pretrain
* generates: PretrainData

Reads pretrain data in TSV format.

```
usage: from-tsv-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i INPUT
                         [INPUT ...] [-c COL] [-n]

Reads pretrain data in TSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the TSV file(s) to read; glob syntax is
                        supported (default: None)
  -c COL, --col_content COL
                        The name (or 1-based index if no header row) of the
                        column with the text content (default: None)
  -n, --no_header       For files with no header row (default: False)
```
