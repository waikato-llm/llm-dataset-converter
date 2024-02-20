# tee

* domain(s): any
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData

Forwards the data passing through to the filter/writer defined as its sub-flow.

```
usage: tee [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-N LOGGER_NAME]
           [-f SUB_FLOW]

Forwards the data passing through to the filter/writer defined as its sub-
flow.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -f SUB_FLOW, --sub_flow SUB_FLOW
                        The command-line defining the subflow
                        (filter(s)/writer). (default: None)
```
