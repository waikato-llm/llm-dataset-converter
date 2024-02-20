# to-xtuner

* domain(s): pairs
* accepts: ldc.api.supervised.pairs.PairData

Writes single-turn conversations in XTuner JSON format (https://github.com/InternLM/xtuner/blob/v0.1.13/docs/en/user_guides/dataset_format.md#single-turn-dialogue-dataset-format).

```
usage: to-xtuner [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                 [-N LOGGER_NAME] -o OUTPUT [--att_instruction ATT]
                 [--att_input ATT] [--att_output ATT] [-p] [-a]

Writes single-turn conversations in XTuner JSON format (https://github.com/Int
ernLM/xtuner/blob/v0.1.13/docs/en/user_guides/dataset_format.md#single-turn-
dialogue-dataset-format).

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT, --output OUTPUT
                        Path of the XTuner file to write (directory when
                        processing multiple files) (default: None)
  --att_instruction ATT
                        The attribute for the instructions (default: None)
  --att_input ATT       The attribute for the inputs (default: None)
  --att_output ATT      The attribute for the outputs (default: None)
  -p, --pretty_print    Whether to output the JSON in more human-readable
                        format. (default: False)
  -a, --ensure_ascii    Whether to ensure that the output is ASCII compatible.
                        (default: False)
```
