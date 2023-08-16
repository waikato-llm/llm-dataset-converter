# to-jsonlines-pretrain

* domain(s): pretrain
* accepts: PretrainData

Writes pretrain data in JsonLines-like JSON format.

```
usage: to-jsonlines-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o
                             OUTPUT [--att_content ATT]

Writes pretrain data in JsonLines-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the JsonLines file to write (directory when
                        processing multiple files) (default: None)
  --att_content ATT     The attribute for the text content (default: None)
```
