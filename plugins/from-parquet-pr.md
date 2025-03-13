# from-parquet-pr

* domain(s): pairs
* generates: ldc.api.supervised.pairs.PairData

Reads prompt/output pairs from Parquet database files.

```
usage: from-parquet-pr [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       [-N LOGGER_NAME] [-i [INPUT ...]] [-I [INPUT_LIST ...]]
                       [--col_instruction COL] [--col_input COL]
                       [--col_output COL] [--col_id COL]
                       [--col_meta [COL ...]]

Reads prompt/output pairs from Parquet database files.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i [INPUT ...], --input [INPUT ...]
                        Path to the parquet file(s) to read; glob syntax is
                        supported; Supported placeholders: {HOME}, {CWD},
                        {TMP} (default: None)
  -I [INPUT_LIST ...], --input_list [INPUT_LIST ...]
                        Path to the text file(s) listing the parquet files to
                        use; Supported placeholders: {HOME}, {CWD}, {TMP}
                        (default: None)
  --col_instruction COL
                        The name of the column with the instructions (default:
                        None)
  --col_input COL       The name of the column with the inputs (default: None)
  --col_output COL      The name of the column with the outputs (default:
                        None)
  --col_id COL          The name of the column with the row IDs (gets stored
                        under 'id' in meta-data) (default: None)
  --col_meta [COL ...]  The name of the columns to store in the meta-data
                        (default: None)
```
