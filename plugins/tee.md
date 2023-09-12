# tee

* domain(s): any
* accepts: PairData, PretrainData, TranslationData
* generates: PairData, PretrainData, TranslationData

Forwards the data passing through to the filter/writer defined as its sub-flow.

```
usage: tee [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-f SUB_FLOW]

Forwards the data passing through to the filter/writer defined as its sub-
flow.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -f SUB_FLOW, --sub_flow SUB_FLOW
                        The command-line defining the subflow
                        (filter(s)/writer). (default: None)
```