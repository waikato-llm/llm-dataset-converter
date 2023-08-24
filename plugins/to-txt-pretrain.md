# to-txt-pretrain

* domain(s): pretrain
* accepts: PretrainData

Writes pretrain data to plain text files.
When providing an output directory, uses the current session counter as the filename.
When providing an output file, all incoming content will be concatenated in this one file.

```
usage: to-txt-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o OUTPUT
                       [-d NUM]

Writes pretrain data to plain text files. When providing an output directory,
uses the current session counter as the filename. When providing an output
file, all incoming content will be concatenated in this one file.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path to the directory or file to write to (default:
                        None)
  -d NUM, --num_digits NUM
                        The number of digits to use for the filenames
                        (default: 6)
```
