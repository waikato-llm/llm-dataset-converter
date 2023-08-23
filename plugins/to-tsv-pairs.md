# to-tsv-pairs

* domain(s): pairs
* accepts: PairData

Writes prompt/output pairs in TSV format.

```
usage: to-tsv-pairs [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o OUTPUT
                    [--col_instruction COL] [--col_input COL]
                    [--col_output COL] [-n]

Writes prompt/output pairs in TSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the TSV file to write (directory when
                        processing multiple files) (default: None)
  --col_instruction COL
                        The name of the column for the instructions (default:
                        None)
  --col_input COL       The name of the column for the inputs (default: None)
  --col_output COL      The name of the column for the outputs (default: None)
  -n, --no_header       For suppressing the header row (default: False)
```
