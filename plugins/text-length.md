# text-length

* domain(s): pairs, pretrain, translation, classification
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData

Keeps or discards data records based on text length constraints. None values get ignored.

```
usage: text-length [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-N LOGGER_NAME] [-m MIN_LENGTH] [-M MAX_LENGTH]
                   [-L [{any,instruction,input,output,content,text} ...]]
                   [-g [LANGUAGE ...]]

Keeps or discards data records based on text length constraints. None values
get ignored.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -m MIN_LENGTH, --min_length MIN_LENGTH
                        The minimum text length, ignored if <0 (default: -1)
  -M MAX_LENGTH, --max_length MAX_LENGTH
                        The maximum text length, ignored if <0 (default: -1)
  -L [{any,instruction,input,output,content,text} ...], --location [{any,instruction,input,output,content,text} ...]
                        Where to apply the checks; classification: any|text,
                        pairs: any|instruction|input|output, pretrain:
                        any|content, translation: any|content (default: any)
  -g [LANGUAGE ...], --language [LANGUAGE ...]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
