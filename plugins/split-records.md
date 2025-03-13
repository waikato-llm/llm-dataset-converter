# split-records

* domain(s): any
* accepts: seppl.AnyData
* generates: seppl.AnyData

Splits the incoming records into the specified split ratios by setting the 'split' meta-data value. Also stores the split names in the current session.

```
usage: split-records [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                     [-N LOGGER_NAME] [-r SPLIT_RATIOS [SPLIT_RATIOS ...]]
                     [-n SPLIT_NAMES [SPLIT_NAMES ...]]

Splits the incoming records into the specified split ratios by setting the
'split' meta-data value. Also stores the split names in the current session.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -r SPLIT_RATIOS [SPLIT_RATIOS ...], --split_ratios SPLIT_RATIOS [SPLIT_RATIOS ...]
                        The split ratios to use for generating the splits
                        (must sum up to 100) (default: None)
  -n SPLIT_NAMES [SPLIT_NAMES ...], --split_names SPLIT_NAMES [SPLIT_NAMES ...]
                        The split names to use for the generated splits, get
                        stored in the meta-data under the key 'split'.
                        (default: None)
```
