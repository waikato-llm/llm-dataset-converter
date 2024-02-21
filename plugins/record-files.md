# record-files

* domain(s): pairs, pretrain, translation
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData

Records the file names in the meta-data ('file') and outputs them, either to a file or stdout.

```
usage: record-files [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                    [-N LOGGER_NAME] [-o OUTPUT_FILE] [-p] [-e]

Records the file names in the meta-data ('file') and outputs them, either to a
file or stdout.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        The file to write the the recorded files to; prints
                        them to stdout if not provided. (default: None)
  -p, --ignore_path     Whether to ignore the path in files when checking
                        against the file list (default: False)
  -e, --ignore_extension
                        Whether to ignore the extension in files when checking
                        against the file list (default: False)
```
