# from-jsonlines-cl

* domain(s): classification
* generates: ldc.api.supervised.classification.ClassificationData

Reads classification data in JsonLines-like JSON format.

```
usage: from-jsonlines-cl [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         [-N LOGGER_NAME] [-i [INPUT [INPUT ...]]]
                         [-I [INPUT_LIST [INPUT_LIST ...]]] [--att_text ATT]
                         [--att_label ATT] [--att_id ATT]
                         [--att_meta [ATT [ATT ...]]] [--encoding ENC]

Reads classification data in JsonLines-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i [INPUT [INPUT ...]], --input [INPUT [INPUT ...]]
                        Path to the JsonLines file(s) to read; glob syntax is
                        supported (default: None)
  -I [INPUT_LIST [INPUT_LIST ...]], --input_list [INPUT_LIST [INPUT_LIST ...]]
                        Path to the text file(s) listing the data files to use
                        (default: None)
  --att_text ATT        The attribute with the text data (default: None)
  --att_label ATT       The attribute with the label (default: None)
  --att_id ATT          The attribute the record ID (gets stored under 'id' in
                        meta-data) (default: None)
  --att_meta [ATT [ATT ...]]
                        The attributes to store in the meta-data (default:
                        None)
  --encoding ENC        The encoding to force instead of auto-detecting it,
                        e.g., 'utf-8' (default: None)
```
