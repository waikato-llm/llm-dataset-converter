# llama2-to-pairs

* domain(s): pairs, pretrain
* accepts: ldc.api.pretrain.PretrainData
* generates: ldc.api.supervised.pairs.PairData

Converts llama2 pretrain records to prompts/response ones. The 'instruction' (ie prompt) is extracted from [INST]...[/INST] and the 'output' (ie response) is the string that follows the [/INST]. Splits on <s> to generate multiple prompt/response records.

```
usage: llama2-to-pairs [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       [-N LOGGER_NAME]

Converts llama2 pretrain records to prompts/response ones. The 'instruction'
(ie prompt) is extracted from [INST]...[/INST] and the 'output' (ie response)
is the string that follows the [/INST]. Splits on <s> to generate multiple
prompt/response records.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
```
