# to-jsonlines-t9n

* domain(s): translation
* accepts: ldc.api.translation.TranslationData

Writes prompt/output pairs in JsonLines-like JSON format. Example: { "translation": { "en": "Others have dismissed him as a joke.", "ro": "Alții l-au numit o glumă." } }

```
usage: to-jsonlines-t9n [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [-N LOGGER_NAME] -o OUTPUT [-d NUM] [-b SIZE]

Writes prompt/output pairs in JsonLines-like JSON format. Example: {
"translation": { "en": "Others have dismissed him as a joke.", "ro": "Alții
l-au numit o glumă." } }

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT, --output OUTPUT
                        Path of the JsonLines file to write (directory when
                        processing multiple files) (default: None)
  -d NUM, --num_digits NUM
                        The number of digits to use for the filenames
                        (default: 6)
  -b SIZE, --buffer_size SIZE
                        The size of the record buffer when concatenating (to
                        improve I/O throughput) (default: 1000)
```
