# to-tsv-pr

* domain(s): pairs
* accepts: ldc.api.supervised.pairs.PairData

Writes prompt/output pairs in TSV format.

```
usage: to-tsv-pr [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                 [-N LOGGER_NAME] [--skip] -o OUTPUT [--col_instruction COL]
                 [--col_input COL] [--col_output COL] [--col_id COL] [-n]
                 [--encoding ENC]

Writes prompt/output pairs in TSV format.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -o OUTPUT, --output OUTPUT
                        Path of the TSV file to write (directory when
                        processing multiple files); Supported placeholders:
                        {HOME}, {CWD}, {TMP} (default: None)
  --col_instruction COL
                        The name of the column for the instructions (default:
                        None)
  --col_input COL       The name of the column for the inputs (default: None)
  --col_output COL      The name of the column for the outputs (default: None)
  --col_id COL          The name of the column for the row IDs (uses 'id' from
                        meta-data) (default: None)
  -n, --no_header       For suppressing the header row (default: False)
  --encoding ENC        The encoding to force instead of using the default,
                        e.g., 'utf-8' (default: None)
```
