# from-tsv-cl

* domain(s): classification
* generates: ldc.api.supervised.classification.ClassificationData

Reads classification data in TSV format.

```
usage: from-tsv-cl [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-N LOGGER_NAME] [-i [INPUT ...]] [-I [INPUT_LIST ...]]
                   [--col_text COL] [--col_label COL] [--col_id COL]
                   [--col_meta [COL ...]] [-n] [--encoding ENC]

Reads classification data in TSV format.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i [INPUT ...], --input [INPUT ...]
                        Path to the TSV file(s) to read; glob syntax is
                        supported; Supported placeholders: {HOME}, {CWD},
                        {TMP} (default: None)
  -I [INPUT_LIST ...], --input_list [INPUT_LIST ...]
                        Path to the text file(s) listing the data files to
                        use; Supported placeholders: {HOME}, {CWD}, {TMP}
                        (default: None)
  --col_text COL        The name of the column (or 1-based index if no header
                        row) with the text (default: None)
  --col_label COL       The name of the column (or 1-based index if no header
                        row) with the labels (default: None)
  --col_id COL          The name (or 1-based index if no header row) of the
                        column with the row IDs (gets stored under 'id' in
                        meta-data) (default: None)
  --col_meta [COL ...]  The name (or 1-based index) of the columns to store in
                        the meta-data (default: None)
  -n, --no_header       For files with no header row (default: False)
  --encoding ENC        The encoding to force instead of auto-detecting it,
                        e.g., 'utf-8' (default: None)
```
