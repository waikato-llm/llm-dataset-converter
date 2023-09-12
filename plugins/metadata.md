# metadata

* domain(s): pairs, pretrain, translation
* accepts: PairData, PretrainData, TranslationData
* generates: PairData, PretrainData, TranslationData

Keeps or discards data records based on meta-data comparisons. Performs the following comparison: METADATA_VALUE COMPARISON VALUE. Records that do not have the required field get discarded automatically.

```
usage: metadata [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-N LOGGER_NAME] -f
                FIELD -v VALUE [-c {lt,le,eq,ne,ge,gt}] [-a {keep,discard}]

Keeps or discards data records based on meta-data comparisons. Performs the
following comparison: METADATA_VALUE COMPARISON VALUE. Records that do not
have the required field get discarded automatically.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -f FIELD, --field FIELD
                        The meta-data field to use in the comparison (default:
                        None)
  -v VALUE, --value VALUE
                        The value to use in the comparison (default: None)
  -c {lt,le,eq,ne,ge,gt}, --comparison {lt,le,eq,ne,ge,gt}
                        How to compare the value with the meta-data value; lt:
                        less than, le: less or equal, eq: equal, ne: not
                        equal, gt: greater than, ge: greater of equal
                        (default: eq)
  -a {keep,discard}, --action {keep,discard}
                        How to react when a keyword is encountered (default:
                        keep)
```
