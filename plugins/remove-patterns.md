# remove-patterns

* domain(s): pairs, pretrain, translation
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData

Removes substrings that match the supplied regular expression patterns.

```
usage: remove-patterns [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       [-N LOGGER_NAME] [-r [EXPR_REMOVE [EXPR_REMOVE ...]]]
                       [-L [{any,instruction,input,output,content} [{any,instruction,input,output,content} ...]]]
                       [-g [LANGUAGE [LANGUAGE ...]]]

Removes substrings that match the supplied regular expression patterns.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -r [EXPR_REMOVE [EXPR_REMOVE ...]], --expr_remove [EXPR_REMOVE [EXPR_REMOVE ...]]
                        Regular expressions for removing sub-strings from the
                        text (gets applied before skipping empty lines); uses
                        re.sub(...). (default: None)
  -L [{any,instruction,input,output,content} [{any,instruction,input,output,content} ...]], --location [{any,instruction,input,output,content} [{any,instruction,input,output,content} ...]]
                        Where to look for the keywords; pairs:
                        any,instruction,input,output, pretrain: any,content,
                        translation: any,content (default: any)
  -g [LANGUAGE [LANGUAGE ...]], --language [LANGUAGE [LANGUAGE ...]]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
