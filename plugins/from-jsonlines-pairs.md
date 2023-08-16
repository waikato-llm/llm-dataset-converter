# from-jsonlines-pairs

* domain(s): pairs
* generates: PairData

Reads prompt/output pairs in JsonLines-like JSON format.

```
usage: from-jsonlines-pairs [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i
                            INPUT [INPUT ...] [--att_instruction ATT]
                            [--att_input ATT] [--att_output ATT]

Reads prompt/output pairs in JsonLines-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the JsonLines file(s) to read; glob syntax is
                        supported (default: None)
  --att_instruction ATT
                        The attribute with the instructions (default: None)
  --att_input ATT       The attribute with the inputs (default: None)
  --att_output ATT      The attribute with the outputs (default: None)
```
