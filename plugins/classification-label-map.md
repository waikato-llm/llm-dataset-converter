# classification-label-map

* domain(s): classification
* accepts: ldc.api.supervised.classification.ClassificationData
* generates: ldc.api.supervised.classification.ClassificationData

Generates a label string/int map and can also replace the label with the integer index.

```
usage: classification-label-map [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                                [-N LOGGER_NAME] [--skip] [-L LABEL_MAP] [-u]

Generates a label string/int map and can also replace the label with the
integer index.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -L LABEL_MAP, --label_map LABEL_MAP
                        The JSON file to store the label map in. Supported
                        placeholders: {HOME}, {CWD}, {TMP} (default: None)
  -u, --update_label    Whether to update the string labels with the integer
                        index. (default: False)
```
