# from-parquet-t9n

* domain(s): translation
* generates: ldc.api.translation.TranslationData

Reads translations from Parquet database files. The translation data must be in JSON format: { "en": "Others have dismissed him as a joke.", "ro": "Alții l-au numit o glumă." }

```
usage: from-parquet-t9n [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [-N LOGGER_NAME] [-i [INPUT [INPUT ...]]]
                        [-I [INPUT_LIST [INPUT_LIST ...]]] [--col_content COL]
                        [--col_id COL] [--col_meta [COL [COL ...]]]

Reads translations from Parquet database files. The translation data must be
in JSON format: { "en": "Others have dismissed him as a joke.", "ro": "Alții
l-au numit o glumă." }

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i [INPUT [INPUT ...]], --input [INPUT [INPUT ...]]
                        Path to the parquet file(s) to read; glob syntax is
                        supported (default: None)
  -I [INPUT_LIST [INPUT_LIST ...]], --input_list [INPUT_LIST [INPUT_LIST ...]]
                        Path to the text file(s) listing the parquet files to
                        use (default: None)
  --col_content COL     The name of the column with the translation data to
                        retrieve (default: None)
  --col_id COL          The name of the column with the row IDs (gets stored
                        under 'id' in meta-data) (default: None)
  --col_meta [COL [COL ...]]
                        The name of the columns to store in the meta-data
                        (default: None)
```
