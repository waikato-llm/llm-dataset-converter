# file-filter

* domain(s): pairs, pretrain, translation
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData

Keeps or discards records based on allow/discard lists for files matched against the 'file' meta-data value.

```
usage: file-filter [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-N LOGGER_NAME] -f FILE_LIST [-a {keep,discard}]
                   [-m {keep,discard}] [-p] [-e]

Keeps or discards records based on allow/discard lists for files matched
against the 'file' meta-data value.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -f FILE_LIST, --file_list FILE_LIST
                        The file containing the files to be kept or discarded
                        (default: None)
  -a {keep,discard}, --action {keep,discard}
                        How to react when a record's 'file' meta-data value
                        matches a filename from the list. (default: keep)
  -m {keep,discard}, --missing_metadata_action {keep,discard}
                        How to react when a record does not have the 'file'
                        meta-data value. (default: keep)
  -p, --ignore_path     Whether to ignore the path in files when checking
                        against the file list (default: False)
  -e, --ignore_extension
                        Whether to ignore the extension in files when checking
                        against the file list (default: False)
```
