# pairs-to-llama2

* domain(s): pairs, pretrain
* accepts: ldc.api.supervised.pairs.PairData
* generates: ldc.api.pretrain.PretrainData

Converts records of prompt/response pairs to llama2-formatted pretrain ones. The 'instruction' (ie prompt) gets wrapped in [INST]...[/INST] and the 'output' (ie response) follows that.

```
usage: pairs-to-llama2 [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       [-N LOGGER_NAME] [--skip] [-p PREFIX]

Converts records of prompt/response pairs to llama2-formatted pretrain ones.
The 'instruction' (ie prompt) gets wrapped in [INST]...[/INST] and the
'output' (ie response) follows that.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -p PREFIX, --prefix PREFIX
                        The prefix to use for the instruction. (default: None)
```
