# update-pair-data

* domain(s): pairs
* accepts: ldc.api.supervised.pairs.PairData
* generates: ldc.api.supervised.pairs.PairData

Updates the pair data according to the format strings, allowing for tweaking or rearranging of the data.

```
usage: update-pair-data [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [-N LOGGER_NAME]
                        [--format_instruction FORMAT_INSTRUCTION]
                        [--format_input FORMAT_INPUT]
                        [--format_output FORMAT_OUTPUT]

Updates the pair data according to the format strings, allowing for tweaking
or rearranging of the data.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --format_instruction FORMAT_INSTRUCTION
                        The format for the instruction content, use
                        placeholder {instruction} for current value; available
                        placeholders:
                        {NEWLINE}|{TAB}|{instruction}|{input}|{output}
                        (default: None)
  --format_input FORMAT_INPUT
                        The format for the input content, use placeholder
                        {input} for current value; available placeholders:
                        {NEWLINE}|{TAB}|{instruction}|{input}|{output}
                        (default: None)
  --format_output FORMAT_OUTPUT
                        The format for the output content, use placeholder
                        {output} for current value; available placeholders:
                        {NEWLINE}|{TAB}|{instruction}|{input}|{output}
                        (default: None)
```
