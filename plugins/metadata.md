# metadata

* domain(s): pairs, pretrain, translation
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData

Keeps or discards data records based on meta-data comparisons. Performs the following comparison: METADATA_VALUE COMPARISON VALUE. Records that do not have the required field get discarded automatically.

```
usage: metadata [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-N LOGGER_NAME]
                [--skip] -f FIELD -v VALUE
                [-c {lt,le,eq,ne,ge,gt,contains,matches}] [-a {keep,discard}]

Keeps or discards data records based on meta-data comparisons. Performs the
following comparison: METADATA_VALUE COMPARISON VALUE. Records that do not
have the required field get discarded automatically.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -f FIELD, --field FIELD
                        The meta-data field to use in the comparison (default:
                        None)
  -v VALUE, --value VALUE
                        The value to use in the comparison (default: None)
  -c {lt,le,eq,ne,ge,gt,contains,matches}, --comparison {lt,le,eq,ne,ge,gt,contains,matches}
                        How to compare the value with the meta-data value; lt:
                        less than, le: less or equal, eq: equal, ne: not
                        equal, gt: greater than, ge: greater of equal,
                        contains: substring match, matches: regexp match; in
                        case of 'contains' and 'matches' the supplied value
                        represents the substring to find/regexp to search with
                        (default: eq)
  -a {keep,discard}, --action {keep,discard}
                        How to react when a keyword is encountered (default:
                        keep)
```
