# pairs-to-pretrain

* domain(s): pairs, pretrain
* accepts: ldc.api.supervised.pairs.PairData
* generates: ldc.api.pretrain.PretrainData

Converts records of prompt/output pairs to pretrain ones.

```
usage: pairs-to-pretrain [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         [-N LOGGER_NAME] [--skip]
                         [-f {instruction,input,output} [{instruction,input,output} ...]]

Converts records of prompt/output pairs to pretrain ones.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -f {instruction,input,output} [{instruction,input,output} ...], --data_fields {instruction,input,output} [{instruction,input,output} ...]
                        The data fields to use for the pretrain content
                        (default: None)
```
