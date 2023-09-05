# skip-duplicate-text

* domain(s): pairs, pretrain, translation
* accepts: PairData, PretrainData, TranslationData
* generates: PairData, PretrainData, TranslationData

Suppresses records with text that has already passed through.

```
usage: skip-duplicate-text [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                           [-L {any,instruction,input,output,content}]
                           [-g [LANGUAGE [LANGUAGE ...]]]

Suppresses records with text that has already passed through.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -L {any,instruction,input,output,content}, --location {any,instruction,input,output,content}
                        Where to look for the keywords; pairs:
                        any,instruction,input,output, pretrain: any,content,
                        translation: any,content (default: any)
  -g [LANGUAGE [LANGUAGE ...]], --language [LANGUAGE [LANGUAGE ...]]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
