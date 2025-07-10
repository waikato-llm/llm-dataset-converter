# set-placeholder

* domain(s): pairs, pretrain, translation
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData

Sets the placeholder to the specified value when data passes through. The value can contain other placeholders, which get expanded each time data passes through.

```
usage: set-placeholder [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       [-N LOGGER_NAME] [--skip] -p PLACEHOLDER -v VALUE

Sets the placeholder to the specified value when data passes through. The
value can contain other placeholders, which get expanded each time data passes
through.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -p PLACEHOLDER, --placeholder PLACEHOLDER
                        The name of the placeholder, without curly brackets.
                        (default: None)
  -v VALUE, --value VALUE
                        The value of the placeholder, may contain other
                        placeholders. Supported placeholders: {INPUT_PATH},
                        {INPUT_NAMEEXT}, {INPUT_NAMENOEXT}, {INPUT_EXT},
                        {INPUT_PARENT_PATH}, {INPUT_PARENT_NAME} (default:
                        None)
```
