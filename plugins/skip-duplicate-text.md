# skip-duplicate-text

* domain(s): pairs, pretrain, translation
* accepts: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData
* generates: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData

Suppresses records with text that has already passed through.

```
usage: skip-duplicate-text [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                           [-N LOGGER_NAME]
                           [-L [{any,instruction,input,output,content} [{any,instruction,input,output,content} ...]]]
                           [-g [LANGUAGE [LANGUAGE ...]]]

Suppresses records with text that has already passed through.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -L [{any,instruction,input,output,content} [{any,instruction,input,output,content} ...]], --location [{any,instruction,input,output,content} [{any,instruction,input,output,content} ...]]
                        Where to look for the keywords; pairs:
                        any,instruction,input,output, pretrain: any,content,
                        translation: any,content (default: any)
  -g [LANGUAGE [LANGUAGE ...]], --language [LANGUAGE [LANGUAGE ...]]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
