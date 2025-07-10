# remove-patterns

* domain(s): pairs, pretrain, translation, classification
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData

Removes substrings that match the supplied regular expression patterns.

```
usage: remove-patterns [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       [-N LOGGER_NAME] [--skip] [-r [EXPR_REMOVE ...]]
                       [-L [{any,instruction,input,output,content,text} ...]]
                       [-g [LANGUAGE ...]]

Removes substrings that match the supplied regular expression patterns.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -r [EXPR_REMOVE ...], --expr_remove [EXPR_REMOVE ...]
                        Regular expressions for removing sub-strings from the
                        text (gets applied before skipping empty lines); uses
                        re.sub(...). (default: None)
  -L [{any,instruction,input,output,content,text} ...], --location [{any,instruction,input,output,content,text} ...]
                        Where to remove the patterns; classification:
                        any|text, pairs: any|instruction|input|output,
                        pretrain: any|content, translation: any|content
                        (default: any)
  -g [LANGUAGE ...], --language [LANGUAGE ...]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
