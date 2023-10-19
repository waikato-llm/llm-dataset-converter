# split

* domain(s): any
* accepts: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData
* generates: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData

Splits the incoming records into the specified split ratios by setting the 'split' meta-data value. Also stores the split names in the current session.

```
usage: split [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-N LOGGER_NAME]
             [-r SPLIT_RATIOS [SPLIT_RATIOS ...]]
             [-n SPLIT_NAMES [SPLIT_NAMES ...]]

Splits the incoming records into the specified split ratios by setting the
'split' meta-data value. Also stores the split names in the current session.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
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
