# from-jsonlines-pt

* domain(s): pretrain
* generates: PretrainData

Reads pretrain data in JsonLines-like JSON format.

```
usage: from-jsonlines-pt [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i INPUT
                         [INPUT ...] [--att_content ATT] [--att_id ATT]

Reads pretrain data in JsonLines-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the JsonLines file(s) to read; glob syntax is
                        supported (default: None)
  --att_content ATT     The attribute with the text content (default: None)
  --att_id ATT          The attribute the record ID (gets stored under 'id' in
                        meta-data) (default: None)
```
