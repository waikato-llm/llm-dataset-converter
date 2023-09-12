# translation-to-pairs

* domain(s): translation, pairs
* accepts: TranslationData
* generates: PairData

Converts records of translation data to pair ones, using specific languages for instruction, input (optional) and output.

```
usage: translation-to-pairs [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                            [-N LOGGER_NAME]
                            [--lang_instruction LANG_INSTRUCTION]
                            [--lang_input LANG_INPUT]
                            [--lang_output LANG_OUTPUT]

Converts records of translation data to pair ones, using specific languages
for instruction, input (optional) and output.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
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
