# remove-blocks

* domain(s): pairs, pretrain, translation
* accepts: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData
* generates: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData

Removes text blocks, using strings identifying start/end of blocks.

```
usage: remove-blocks [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                     [-N LOGGER_NAME]
                     [--block_removal_start [BLOCK_REMOVAL_START [BLOCK_REMOVAL_START ...]]]
                     [--block_removal_end [BLOCK_REMOVAL_END [BLOCK_REMOVAL_END ...]]]
                     [-L {any,instruction,input,output,content}]
                     [-g [LANGUAGE [LANGUAGE ...]]]

Removes text blocks, using strings identifying start/end of blocks.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --block_removal_start [BLOCK_REMOVAL_START [BLOCK_REMOVAL_START ...]]
                        The starting strings for blocks to remove (default:
                        None)
  --block_removal_end [BLOCK_REMOVAL_END [BLOCK_REMOVAL_END ...]]
                        The ending strings for blocks to remove (default:
                        None)
  -L {any,instruction,input,output,content}, --location {any,instruction,input,output,content}
                        Where to look for the keywords; pairs:
                        any,instruction,input,output, pretrain: any,content,
                        translation: any,content (default: any)
  -g [LANGUAGE [LANGUAGE ...]], --language [LANGUAGE [LANGUAGE ...]]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
