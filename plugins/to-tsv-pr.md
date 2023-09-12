# to-tsv-pr

* domain(s): pairs
* accepts: PairData

Writes prompt/output pairs in TSV format.

```
usage: to-tsv-pr [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-N LOGGER_NAME]
                 -o OUTPUT [--col_instruction COL] [--col_input COL]
                 [--col_output COL] [--col_id COL] [-n]

Writes prompt/output pairs in TSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT, --output OUTPUT
                        Path of the TSV file to write (directory when
                        processing multiple files) (default: None)
  --col_instruction COL
                        The name of the column for the instructions (default:
                        None)
  --col_input COL       The name of the column for the inputs (default: None)
  --col_output COL      The name of the column for the outputs (default: None)
  --col_id COL          The name of the column for the row IDs (uses 'id' from
                        meta-data) (default: None)
  -n, --no_header       For suppressing the header row (default: False)
```
