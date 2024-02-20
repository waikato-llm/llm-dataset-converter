# to-jsonlines-cl

* domain(s): classification
* accepts: ldc.api.supervised.classification.ClassificationData

Writes classification data in JsonLines-like JSON format.

```
usage: to-jsonlines-cl [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       [-N LOGGER_NAME] -o OUTPUT [--att_text ATT]
                       [--att_label ATT] [--att_id ATT] [-d NUM] [-b SIZE]

Writes classification data in JsonLines-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT, --output OUTPUT
                        Path of the JsonLines file to write (directory when
                        processing multiple files) (default: None)
  --att_text ATT        The attribute for the text data (default: None)
  --att_label ATT       The attribute for the label (default: None)
  --att_id ATT          The name of the attribute for the row IDs (uses 'id'
                        from meta-data) (default: None)
  -d NUM, --num_digits NUM
                        The number of digits to use for the filenames
                        (default: 6)
  -b SIZE, --buffer_size SIZE
                        The size of the record buffer when concatenating (to
                        improve I/O throughput) (default: 1000)
```
