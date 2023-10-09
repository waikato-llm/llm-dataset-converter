# require-languages

* domain(s): translation
* accepts: ldc.translation.TranslationData
* generates: ldc.translation.TranslationData

Discards records if the required languages aren't present.

```
usage: require-languages [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                         [-N LOGGER_NAME] -g LANGUAGE [LANGUAGE ...]

Discards records if the required languages aren't present.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -g LANGUAGE [LANGUAGE ...], --language LANGUAGE [LANGUAGE ...]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
