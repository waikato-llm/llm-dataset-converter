# to-txt-pretrain

* domain(s): pretrain
* accepts: PretrainData

Writes pretrain data to plain text files. Uses the current session counter for the filename.

```
usage: to-txt-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o OUTPUT
                       [-d NUM]

Writes pretrain data to plain text files. Uses the current session counter for
the filename.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path to the directory to write to (default: None)
  -d NUM, --num_digits NUM
                        The number of digits to use for the filenames
                        (default: 6)
```
