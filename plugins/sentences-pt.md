# sentences-pt

* domain(s): pretrain
* accepts: ldc.api.pretrain.PretrainData
* generates: ldc.api.pretrain.PretrainData

Splits pretrain text data into sentences and puts them on separate lines (using new-lines).

```
usage: sentences-pt [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                    [-N LOGGER_NAME] [-c END_CHARS] [-q QUOTE_CHARS]
                    [-m MAX_SENTENCES] [-s]

Splits pretrain text data into sentences and puts them on separate lines
(using new-lines).

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -c END_CHARS, --end_chars END_CHARS
                        The characters signifying the end of a sentence.
                        (default: .!?;:))
  -q QUOTE_CHARS, --quote_chars QUOTE_CHARS
                        The characters that represent quotes. (default: "'”’)
  -m MAX_SENTENCES, --max_sentences MAX_SENTENCES
                        The maximum number of sentences per line. (default: 1)
  -s, --split_records   Splits the lines into separate records (one line per
                        record) after reassambling the lines instead of
                        combining them back into single document. (default:
                        False)
```
