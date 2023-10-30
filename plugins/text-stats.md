# text-stats

* domain(s): pairs, pretrain, translation
* accepts: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData
* generates: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData

Computes basic statics from the textual data passing through.

```
usage: text-stats [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-N LOGGER_NAME]
                  [-o OUTPUT] [-d] [-L {any,instruction,input,output,content}]
                  [-g [LANGUAGE [LANGUAGE ...]]]

Computes basic statics from the textual data passing through.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT, --output OUTPUT
                        The JSON file to store the statistics in; outputs a
                        textual representation on stdout when missing
                        (default: None)
  -d, --detailed        Whether to output more detailed statistics, e.g., the
                        counts per string length (default: False)
  -L {any,instruction,input,output,content}, --location {any,instruction,input,output,content}
                        Where to look for the text; pairs:
                        any,instruction,input,output, pretrain: any,content,
                        translation: any,content (default: any)
  -g [LANGUAGE [LANGUAGE ...]], --language [LANGUAGE [LANGUAGE ...]]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
