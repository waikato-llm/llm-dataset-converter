# from-jsonlines-pt

* domain(s): pretrain
* generates: ldc.api.pretrain.PretrainData

Reads pretrain data in JsonLines-like JSON format.

```
usage: from-jsonlines-pt [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         [-N LOGGER_NAME] [-i [INPUT ...]]
                         [-I [INPUT_LIST ...]] [--att_content ATT]
                         [--att_id ATT] [--att_meta [ATT ...]]
                         [--encoding ENC]

Reads pretrain data in JsonLines-like JSON format.

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
  --att_content ATT     The attribute with the text content (default: None)
  --att_id ATT          The attribute the record ID (gets stored under 'id' in
                        meta-data) (default: None)
  --att_meta [ATT ...]  The attributes to store in the meta-data (default:
                        None)
  --encoding ENC        The encoding to force instead of auto-detecting it,
                        e.g., 'utf-8' (default: None)
```
