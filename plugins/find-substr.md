# find-substr

* domain(s): pairs, pretrain, translation, classification
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData

Keeps or discards data records based on sub-string(s) text matching. Search is performed in lower-case. Optionally, the sub-strings can represent regular expressions used for searching the strings.

```
usage: find-substr [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-N LOGGER_NAME] -s SUB_STRING [SUB_STRING ...] [-r]
                   [-L [{any,instruction,input,output,content,text} ...]]
                   [-g [LANGUAGE ...]] [-a {keep,discard}]

Keeps or discards data records based on sub-string(s) text matching. Search is
performed in lower-case. Optionally, the sub-strings can represent regular
expressions used for searching the strings.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -s SUB_STRING [SUB_STRING ...], --sub_string SUB_STRING [SUB_STRING ...]
                        The substrings to look for (lower case) (default:
                        None)
  -r, --is_regexp       Whether the sub-strings represent regular expressions
                        (default: False)
  -L [{any,instruction,input,output,content,text} ...], --location [{any,instruction,input,output,content,text} ...]
                        Where to look for the substrings; classification:
                        any|text, pairs: any|instruction|input|output,
                        pretrain: any|content, translation: any|content
                        (default: any)
  -g [LANGUAGE ...], --language [LANGUAGE ...]
                        The languages to inspect; inspects all if not
                        specified (default: None)
  -a {keep,discard}, --action {keep,discard}
                        How to react when a substring is found (default: keep)
```
