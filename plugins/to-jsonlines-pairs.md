# to-jsonlines-pairs

* domain(s): pairs
* accepts: PairData

Writes prompt/output pairs in JsonLines-like JSON format.

```
usage: to-jsonlines-pairs [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o OUTPUT
                          [--att_instruction ATT] [--att_input ATT]
                          [--att_output ATT]

Writes prompt/output pairs in JsonLines-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the JsonLines file to write (directory when
                        processing multiple files) (default: None)
  --att_instruction ATT
                        The attribute for the instructions (default: None)
  --att_input ATT       The attribute for the inputs (default: None)
  --att_output ATT      The attribute for the outputs (default: None)
```
