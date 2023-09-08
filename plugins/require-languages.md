# require-languages

* domain(s): translation
* accepts: TranslationData
* generates: TranslationData

Discards records if the required languages aren't present.

```
usage: require-languages [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -g
                         LANGUAGE [LANGUAGE ...]

Discards records if the required languages aren't present.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -g LANGUAGE [LANGUAGE ...], --language LANGUAGE [LANGUAGE ...]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
