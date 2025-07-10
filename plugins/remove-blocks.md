# remove-blocks

* domain(s): pairs, pretrain, translation, classification
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData

Removes text blocks, using strings identifying start/end of blocks.

```
usage: remove-blocks [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                     [-N LOGGER_NAME] [--skip]
                     [--block_removal_start [BLOCK_REMOVAL_START ...]]
                     [--block_removal_end [BLOCK_REMOVAL_END ...]]
                     [-L [{any,instruction,input,output,content,text} ...]]
                     [-g [LANGUAGE ...]]

Removes text blocks, using strings identifying start/end of blocks.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  --block_removal_start [BLOCK_REMOVAL_START ...]
                        The starting strings for blocks to remove (default:
                        None)
  --block_removal_end [BLOCK_REMOVAL_END ...]
                        The ending strings for blocks to remove (default:
                        None)
  -L [{any,instruction,input,output,content,text} ...], --location [{any,instruction,input,output,content,text} ...]
                        Where to remove the blocks; classification: any|text,
                        pairs: any|instruction|input|output, pretrain:
                        any|content, translation: any|content (default: any)
  -g [LANGUAGE ...], --language [LANGUAGE ...]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
