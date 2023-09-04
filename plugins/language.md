# language

* domain(s): translation
* accepts: TranslationData
* generates: TranslationData

Keeps or discards languages.

```
usage: language [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -L LANGUAGE
                [LANGUAGE ...] [-a {keep,discard}]

Keeps or discards languages.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -L LANGUAGE [LANGUAGE ...], --language LANGUAGE [LANGUAGE ...]
                        The languages to look for (default: None)
  -a {keep,discard}, --action {keep,discard}
                        How to react when a language is encountered (default:
                        keep)
```
