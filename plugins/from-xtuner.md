# from-xtuner

* domain(s): pairs
* generates: ldc.api.supervised.pairs.PairData

Reads single-turn conversations in XTuner JSON format (https://github.com/InternLM/xtuner/blob/v0.1.13/docs/en/user_guides/dataset_format.md#single-turn-dialogue-dataset-format).

```
usage: from-xtuner [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-N LOGGER_NAME] [-i [INPUT ...]] [-I [INPUT_LIST ...]]
                   [--att_system ATT] [--att_input ATT] [--att_output ATT]
                   [--encoding ENC]

Reads single-turn conversations in XTuner JSON format (https://github.com/Inte
rnLM/xtuner/blob/v0.1.13/docs/en/user_guides/dataset_format.md#single-turn-
dialogue-dataset-format).

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i [INPUT ...], --input [INPUT ...]
                        Path to the XTuner file(s) to read; glob syntax is
                        supported; Supported placeholders: {HOME}, {CWD},
                        {TMP} (default: None)
  -I [INPUT_LIST ...], --input_list [INPUT_LIST ...]
                        Path to the text file(s) listing the XTuner files to
                        use; Supported placeholders: {HOME}, {CWD}, {TMP}
                        (default: None)
  --att_system ATT      The attribute with the system instructions (default:
                        None)
  --att_input ATT       The attribute with the inputs (default: None)
  --att_output ATT      The attribute with the outputs (default: None)
  --encoding ENC        The encoding to force instead of auto-detecting it,
                        e.g., 'utf-8' (default: None)
```
