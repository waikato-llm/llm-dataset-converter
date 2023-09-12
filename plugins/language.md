# language

* domain(s): translation
* accepts: TranslationData
* generates: TranslationData

Keeps or discards languages.

```
usage: language [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-N LOGGER_NAME] -g
                LANGUAGE [LANGUAGE ...] [-a {keep,discard}]

Keeps or discards languages.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -g LANGUAGE [LANGUAGE ...], --language LANGUAGE [LANGUAGE ...]
                        The languages to look for (default: None)
  -a {keep,discard}, --action {keep,discard}
                        How to react when a language is encountered (default:
                        keep)
```
