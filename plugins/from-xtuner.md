# from-xtuner

* domain(s): pairs
* generates: ldc.api.supervised.pairs.PairData

Reads single-turn conversations in XTuner JSON format (https://github.com/InternLM/xtuner/blob/v0.1.13/docs/en/user_guides/dataset_format.md#single-turn-dialogue-dataset-format).

```
usage: from-xtuner [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-N LOGGER_NAME] [-i [INPUT [INPUT ...]]]
                   [-I [INPUT_LIST [INPUT_LIST ...]]] [--att_instruction ATT]
                   [--att_input ATT] [--att_output ATT] [--encoding ENC]

Reads single-turn conversations in XTuner JSON format (https://github.com/Inte
rnLM/xtuner/blob/v0.1.13/docs/en/user_guides/dataset_format.md#single-turn-
dialogue-dataset-format).

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i [INPUT [INPUT ...]], --input [INPUT [INPUT ...]]
                        Path to the XTuner file(s) to read; glob syntax is
                        supported (default: None)
  -I [INPUT_LIST [INPUT_LIST ...]], --input_list [INPUT_LIST [INPUT_LIST ...]]
                        Path to the text file(s) listing the data files to use
                        (default: None)
  --att_instruction ATT
                        The attribute with the instructions (default: None)
  --att_input ATT       The attribute with the inputs (default: None)
  --att_output ATT      The attribute with the outputs (default: None)
  --encoding ENC        The encoding to force instead of auto-detecting it,
                        e.g., 'utf-8' (default: None)
```
