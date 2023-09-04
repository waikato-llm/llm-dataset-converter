# translation-to-pretrain

* domain(s): translation, pretrain
* accepts: TranslationData
* generates: PretrainData

Converts records of translation data to pretrain ones, extracting a specific language.

```
usage: translation-to-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                               [--lang LANG]

Converts records of translation data to pretrain ones, extracting a specific
language.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  --lang LANG           The ID of the language to convert (default: None)
```
