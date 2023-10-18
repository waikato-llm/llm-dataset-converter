# from-tsv-pr

* domain(s): pairs
* generates: ldc.supervised.pairs.PairData

Reads prompt/output pairs in TSV format.

```
usage: from-tsv-pr [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-N LOGGER_NAME]
                   -i INPUT [INPUT ...] [--col_instruction COL]
                   [--col_input COL] [--col_output COL] [--col_id COL]
                   [--col_meta [COL [COL ...]]] [-n]

Reads prompt/output pairs in TSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the TSV file(s) to read; glob syntax is
                        supported (default: None)
  --col_instruction COL
                        The name of the column (or 1-based index if no header
                        row) with the instructions (default: None)
  --col_input COL       The name of the column (or 1-based index if no header
                        row) with the inputs (default: None)
  --col_output COL      The name of the column (or 1-based index if no header
                        row) with the outputs (default: None)
  --col_id COL          The name (or 1-based index if no header row) of the
                        column with the row IDs (gets stored under 'id' in
                        meta-data) (default: None)
  --col_meta [COL [COL ...]]
                        The name (or 1-based index) of the columns to store in
                        the meta-data (default: None)
  -n, --no_header       For files with no header row (default: False)
```
