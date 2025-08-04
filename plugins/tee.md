# tee

* domain(s): any
* accepts: seppl.AnyData
* generates: seppl.AnyData

Forwards the data passing through to the filter/writer defined as its sub-flow.When supplying a meta-data field and a value, this can be turned into a conditional forwarding. Performs the following comparison: METADATA_VALUE COMPARISON VALUE.

```
usage: tee [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-N LOGGER_NAME]
           [--skip] [-f SUB_FLOW] [--field FIELD] [--value VALUE]
           [--comparison {lt,le,eq,ne,ge,gt,contains,matches}]

Forwards the data passing through to the filter/writer defined as its sub-
flow.When supplying a meta-data field and a value, this can be turned into a
conditional forwarding. Performs the following comparison: METADATA_VALUE
COMPARISON VALUE.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -f SUB_FLOW, --sub_flow SUB_FLOW
                        The command-line defining the subflow
                        (filter(s)/writer). (default: None)
  --field FIELD         The meta-data field to use in the comparison (default:
                        None)
  --value VALUE         The value to use in the comparison (default: None)
  --comparison {lt,le,eq,ne,ge,gt,contains,matches}
                        How to compare the value with the meta-data value; lt:
                        less than, le: less or equal, eq: equal, ne: not
                        equal, gt: greater than, ge: greater of equal,
                        contains: substring match, matches: regexp match; in
                        case of 'contains' and 'matches' the supplied value
                        represents the substring to find/regexp to search with
                        (default: eq)
```
