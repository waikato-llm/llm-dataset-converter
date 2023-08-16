# pairs-to-pretrain

* domain(s): pairs, pretrain
* accepts: PairData
* generates: PretrainData

Converts records of prompt/output pairs to pretrain ones.

```
usage: pairs-to-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                         [-f {instruction,input,output} [{instruction,input,output} ...]]

Converts records of prompt/output pairs to pretrain ones.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -f {instruction,input,output} [{instruction,input,output} ...], --data_fields {instruction,input,output} [{instruction,input,output} ...]
                        The data fields to use for the pretrain content
                        (default: None)
```
