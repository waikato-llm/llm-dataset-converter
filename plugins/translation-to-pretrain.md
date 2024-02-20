# translation-to-pretrain

* domain(s): translation, pretrain
* accepts: ldc.api.translation.TranslationData
* generates: ldc.api.pretrain.PretrainData

Converts records of translation data to pretrain ones, extracting a specific language.

```
usage: translation-to-pretrain [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                               [-N LOGGER_NAME] [--lang LANG]

Converts records of translation data to pretrain ones, extracting a specific
language.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --lang LANG           The ID of the language to convert (default: None)
```
