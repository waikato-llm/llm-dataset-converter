# to-llama2-format

* domain(s): pretrain
* accepts: ldc.pretrain.PretrainData
* generates: ldc.pretrain.PretrainData

Turns pretrain records into llama2 format (without the [INST]...[/INST] block).

```
usage: to-llama2-format [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [-N LOGGER_NAME]

Turns pretrain records into llama2 format (without the [INST]...[/INST]
block).

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
```
