# strip-strings

* domain(s): pairs, pretrain, translation, classification
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData

Strips whitespaces from start/end of strings.

```
usage: strip-strings [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                     [-N LOGGER_NAME] [--skip]
                     [-L [{any,instruction,input,output,content,text} ...]]
                     [-g [LANGUAGE ...]]

Strips whitespaces from start/end of strings.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -L [{any,instruction,input,output,content,text} ...], --location [{any,instruction,input,output,content,text} ...]
                        Which strings to strip; classification: any|text,
                        pairs: any|instruction|input|output, pretrain:
                        any|content, translation: any|content (default: any)
  -g [LANGUAGE ...], --language [LANGUAGE ...]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
