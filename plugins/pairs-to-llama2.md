# pairs-to-llama2

* domain(s): pairs, pretrain
* accepts: ldc.supervised.pairs.PairData
* generates: ldc.pretrain.PretrainData

Converts records of prompt/output pairs to llama2 pretrain ones. The 'instruction' (ie prompt) gets wrapped in [INST]...[/INST] and the 'output' (ie response) follows that.

```
usage: pairs-to-llama2 [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                       [-N LOGGER_NAME] [-p PREFIX]

Converts records of prompt/output pairs to llama2 pretrain ones. The
'instruction' (ie prompt) gets wrapped in [INST]...[/INST] and the 'output'
(ie response) follows that.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -p PREFIX, --prefix PREFIX
                        The prefix to use for the instruction. (default: None)
```
