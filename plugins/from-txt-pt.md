# from-txt-pt

* domain(s): pretrain
* generates: PretrainData

Reads pretrain data from plain text files, with each file representing a data record.
Text files can be split into lines and forwarded as separate records as well.

```
usage: from-txt-pt [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i INPUT
                   [INPUT ...] [-s] [-e]

Reads pretrain data from plain text files, with each file representing a data
record. Text files can be split into lines and forwarded as separate records
as well.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the text file(s) to read; glob syntax is
                        supported (default: None)
  -s, --split_lines     Splits the text file on new lines and forwards them as
                        separate records; the index of the line gets stored in
                        the meta-data under 'line'. (default: False)
  -e, --skip_empty      Removes empty lines from the data. (default: False)
```
