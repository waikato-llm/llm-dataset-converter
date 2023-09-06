# from-jsonlines-t9n

* domain(s): translation
* generates: TranslationData

Reads translation in JsonLines-like JSON format. Example: { "translation": { "en": "Others have dismissed him as a joke.", "ro": "Alții l-au numit o glumă." } }

```
usage: from-jsonlines-t9n [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i INPUT
                          [INPUT ...]

Reads translation in JsonLines-like JSON format. Example: { "translation": {
"en": "Others have dismissed him as a joke.", "ro": "Alții l-au numit o
glumă." } }

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the JsonLines file(s) to read; glob syntax is
                        supported (default: None)
```
