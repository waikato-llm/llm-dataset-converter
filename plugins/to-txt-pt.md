# to-txt-pt

* domain(s): pretrain
* accepts: ldc.pretrain.PretrainData

Writes pretrain data to plain text files.
When providing an output directory, either uses the current session counter as the filename or, if present, the 'id' value from the meta-data.
When providing an output file, all incoming content will be concatenated in this one file. Compression is not available in this case due to the streaming context.

```
usage: to-txt-pt [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-N LOGGER_NAME]
                 -o OUTPUT [-d NUM] [-b SIZE]

Writes pretrain data to plain text files. When providing an output directory,
either uses the current session counter as the filename or, if present, the
'id' value from the meta-data. When providing an output file, all incoming
content will be concatenated in this one file. Compression is not available in
this case due to the streaming context.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT, --output OUTPUT
                        Path to the directory or file to write to (default:
                        None)
  -d NUM, --num_digits NUM
                        The number of digits to use for the filenames
                        (default: 6)
  -b SIZE, --buffer_size SIZE
                        The size of the record buffer when concatenating (to
                        improve I/O throughput) (default: 1000)
```
