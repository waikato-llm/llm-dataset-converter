# replace-patterns

* domain(s): pairs, pretrain, translation
* accepts: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData
* generates: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData

Replaces substrings that match regular expressions patterns.

```
usage: replace-patterns [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [-N LOGGER_NAME] [-f [FIND [FIND ...]]]
                        [-r [REPLACE [REPLACE ...]]]
                        [-L [{any,instruction,input,output,content} [{any,instruction,input,output,content} ...]]]
                        [-g [LANGUAGE [LANGUAGE ...]]]

Replaces substrings that match regular expressions patterns.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -f [FIND [FIND ...]], --find [FIND [FIND ...]]
                        Regular expressions for replacing sub-strings in the
                        text (gets applied before skipping empty lines); uses
                        re.sub(...). (default: None)
  -r [REPLACE [REPLACE ...]], --replace [REPLACE [REPLACE ...]]
                        The corresponding replacement strings. (default: None)
  -L [{any,instruction,input,output,content} [{any,instruction,input,output,content} ...]], --location [{any,instruction,input,output,content} [{any,instruction,input,output,content} ...]]
                        Where to look for the keywords; pairs:
                        any,instruction,input,output, pretrain: any,content,
                        translation: any,content (default: any)
  -g [LANGUAGE [LANGUAGE ...]], --language [LANGUAGE [LANGUAGE ...]]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
