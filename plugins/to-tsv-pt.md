# to-tsv-pt

* domain(s): pretrain
* accepts: ldc.api.pretrain.PretrainData

Writes pretrain data in TSV format.

```
usage: to-tsv-pt [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                 [-N LOGGER_NAME] [--skip] -o OUTPUT [-c COL] [--col_id COL]
                 [-n] [-s] [--encoding ENC]

Writes pretrain data in TSV format.

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
  -c COL, --col_content COL
                        The name of the column for the content when outputting
                        a header row (default: None)
  --col_id COL          The name of the column for the row IDs (uses 'id' from
                        meta-data) (default: None)
  -n, --no_header       For suppressing the header row (default: False)
  -s, --split_lines     Splits the text content on new lines and stores them
                        as separate records. (default: False)
  --encoding ENC        The encoding to force instead of using the default,
                        e.g., 'utf-8' (default: None)
```
