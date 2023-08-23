# keyword-pretrain

* domain(s): pretrain
* accepts: PretrainData
* generates: PretrainData

Keeps or discards data records based on keyword(s).

```
usage: keyword-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -k KEYWORD
                        [KEYWORD ...] [-L {any,content}] [-a {keep,discard}]

Keeps or discards data records based on keyword(s).

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -k KEYWORD [KEYWORD ...], --keyword KEYWORD [KEYWORD ...]
                        The keywords to look for (default: None)
  -L {any,content}, --location {any,content}
                        Where to look for the keywords (default: any)
  -a {keep,discard}, --action {keep,discard}
                        How to react when a keyword is encountered (default:
                        keep)
```
