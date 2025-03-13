# from-jsonlines-t9n

* domain(s): translation
* generates: ldc.api.translation.TranslationData

Reads translation in JsonLines-like JSON format. Example: { "translation": { "en": "Others have dismissed him as a joke.", "ro": "Alții l-au numit o glumă." } }

```
usage: from-jsonlines-t9n [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                          [-N LOGGER_NAME] [-i [INPUT ...]]
                          [-I [INPUT_LIST ...]] [--att_meta [ATT ...]]
                          [--encoding ENC]

Reads translation in JsonLines-like JSON format. Example: { "translation": {
"en": "Others have dismissed him as a joke.", "ro": "Alții l-au numit o
glumă." } }

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i [INPUT ...], --input [INPUT ...]
                        Path to the JsonLines file(s) to read; glob syntax is
                        supported; Supported placeholders: {HOME}, {CWD},
                        {TMP} (default: None)
  -I [INPUT_LIST ...], --input_list [INPUT_LIST ...]
                        Path to the text file(s) listing the JsonLines files
                        to use; Supported placeholders: {HOME}, {CWD}, {TMP}
                        (default: None)
  --att_meta [ATT ...]  The attributes to store in the meta-data (default:
                        None)
  --encoding ENC        The encoding to force instead of auto-detecting it,
                        e.g., 'utf-8' (default: None)
```
