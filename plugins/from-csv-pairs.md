# from-csv-pairs

* domain(s): pairs
* generates: PairData

Reads prompt/output pairs in CSV format.

```
usage: from-csv-pairs [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i INPUT
                      [INPUT ...] [--col_instruction COL] [--col_input COL]
                      [--col_output COL] [-n]

Reads prompt/output pairs in CSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the CSV file(s) to read; glob syntax is
                        supported (default: None)
  --col_instruction COL
                        The name of the column (or 1-based index if no header
                        row) with the instructions (default: None)
  --col_input COL       The name of the column (or 1-based index if no header
                        row) with the inputs (default: None)
  --col_output COL      The name of the column (or 1-based index if no header
                        row) with the outputs (default: None)
  -n, --no_header       For files with no header row (default: False)
```
