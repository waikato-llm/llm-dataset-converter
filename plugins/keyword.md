# keyword

* domain(s): pairs, pretrain, translation, classification
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData

Keeps or discards data records based on keyword(s). Search is performed in lower-case.

```
usage: keyword [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-N LOGGER_NAME]
               [--skip] -k KEYWORD [KEYWORD ...]
               [-L [{any,instruction,input,output,content,text} ...]]
               [-g [LANGUAGE ...]] [-a {keep,discard}]

Keeps or discards data records based on keyword(s). Search is performed in
lower-case.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -k KEYWORD [KEYWORD ...], --keyword KEYWORD [KEYWORD ...]
                        The keywords to look for (lower case) (default: None)
  -L [{any,instruction,input,output,content,text} ...], --location [{any,instruction,input,output,content,text} ...]
                        Where to look for the keywords; classification:
                        any|text, pairs: any|instruction|input|output,
                        pretrain: any|content, translation: any|content
                        (default: any)
  -g [LANGUAGE ...], --language [LANGUAGE ...]
                        The languages to inspect; inspects all if not
                        specified (default: None)
  -a {keep,discard}, --action {keep,discard}
                        How to react when a keyword is encountered (default:
                        keep)
```
