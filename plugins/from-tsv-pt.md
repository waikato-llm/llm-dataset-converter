# from-tsv-pt

* domain(s): pretrain
* generates: ldc.pretrain.PretrainData

Reads pretrain data in TSV format.

```
usage: from-tsv-pt [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-N LOGGER_NAME] [-i [INPUT [INPUT ...]]]
                   [-I [INPUT_LIST [INPUT_LIST ...]]] [-c COL] [--col_id COL]
                   [--col_meta [COL [COL ...]]] [-n] [--encoding ENC]

Reads pretrain data in TSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i [INPUT [INPUT ...]], --input [INPUT [INPUT ...]]
                        Path to the TSV file(s) to read; glob syntax is
                        supported (default: None)
  -I [INPUT_LIST [INPUT_LIST ...]], --input_list [INPUT_LIST [INPUT_LIST ...]]
                        Path to the text file(s) listing the data files to use
                        (default: None)
  -c COL, --col_content COL
                        The name (or 1-based index if no header row) of the
                        column with the text content (default: None)
  --col_id COL          The name (or 1-based index if no header row) of the
                        column with the row IDs (gets stored under 'id' in
                        meta-data) (default: None)
  --col_meta [COL [COL ...]]
                        The name (or 1-based index) of the columns to store in
                        the meta-data (default: None)
  -n, --no_header       For files with no header row (default: False)
  --encoding ENC        The encoding to force instead of auto-detecting it,
                        e.g., 'utf-8' (default: None)
```
