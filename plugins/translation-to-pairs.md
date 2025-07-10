# translation-to-pairs

* domain(s): translation, pairs
* accepts: ldc.api.translation.TranslationData
* generates: ldc.api.supervised.pairs.PairData

Converts records of translation data to pair ones, using specific languages for instruction, input (optional) and output.

```
usage: translation-to-pairs [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                            [-N LOGGER_NAME] [--skip]
                            [--lang_instruction LANG_INSTRUCTION]
                            [--lang_input LANG_INPUT]
                            [--lang_output LANG_OUTPUT]

Converts records of translation data to pair ones, using specific languages
for instruction, input (optional) and output.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  --lang_instruction LANG_INSTRUCTION
                        The ID of the language to use for the instruction
                        (default: None)
  --lang_input LANG_INPUT
                        The ID of the language to use for the input (optional)
                        (default: None)
  --lang_output LANG_OUTPUT
                        The ID of the language to use for the output (default:
                        None)
```
