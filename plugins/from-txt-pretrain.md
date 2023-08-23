# from-txt-pretrain

* domain(s): pretrain
* generates: PretrainData

Reads pretrain data from plain text files, with each file representing a data record.

```
usage: from-txt-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i INPUT
                         [INPUT ...]

Reads pretrain data from plain text files, with each file representing a data
record.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the text file(s) to read; glob syntax is
                        supported (default: None)
```
