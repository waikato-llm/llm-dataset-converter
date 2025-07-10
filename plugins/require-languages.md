# require-languages

* domain(s): translation
* accepts: ldc.api.translation.TranslationData
* generates: ldc.api.translation.TranslationData

Discards records if the required languages aren't present.

```
usage: require-languages [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         [-N LOGGER_NAME] [--skip] -g LANGUAGE [LANGUAGE ...]

Discards records if the required languages aren't present.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -g LANGUAGE [LANGUAGE ...], --language LANGUAGE [LANGUAGE ...]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
