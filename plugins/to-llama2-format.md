# to-llama2-format

* domain(s): pretrain
* accepts: ldc.api.pretrain.PretrainData
* generates: ldc.api.pretrain.PretrainData

Turns pretrain records into llama2 format. Based on: https://github.com/facebookresearch/llama/blob/ef351e9cd9496c579bf9f2bb036ef11bdc5ca3d2/llama/generation.py#L320

```
usage: to-llama2-format [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [-N LOGGER_NAME] [--skip_tokens]

Turns pretrain records into llama2 format. Based on: https://github.com/facebo
okresearch/llama/blob/ef351e9cd9496c579bf9f2bb036ef11bdc5ca3d2/llama/generatio
n.py#L320

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip_tokens         Whether to leave out the [INST] [/INST] tokens
                        (default: False)
```
