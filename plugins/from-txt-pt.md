# from-txt-pt

* domain(s): pretrain
* generates: ldc.pretrain.PretrainData

Reads pretrain data from plain text files, with each file representing a data record.
Text files can be split into lines and forwarded as separate records as well.

```
usage: from-txt-pt [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-N LOGGER_NAME]
                   -i INPUT [INPUT ...] [-s]
                   [-r [EXPR_REMOVE [EXPR_REMOVE ...]]] [-e] [--sentences]
                   [-c END_CHARS] [-q QUOTE_CHARS]
                   [--block_removal_start [BLOCK_REMOVAL_START [BLOCK_REMOVAL_START ...]]]
                   [--block_removal_end [BLOCK_REMOVAL_END [BLOCK_REMOVAL_END ...]]]
                   [-m MAX_SENTENCES]

Reads pretrain data from plain text files, with each file representing a data
record. Text files can be split into lines and forwarded as separate records
as well.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the text file(s) to read; glob syntax is
                        supported (default: None)
  -s, --split_lines     Splits the text file on new lines and forwards them as
                        separate records; the index of the line gets stored in
                        the meta-data under 'line'. (default: False)
  -r [EXPR_REMOVE [EXPR_REMOVE ...]], --expr_remove [EXPR_REMOVE [EXPR_REMOVE ...]]
                        Regular expressions for removing sub-strings from the
                        text (gets applied before skipping empty lines); uses
                        re.sub(...). (default: None)
  -e, --skip_empty      Removes empty lines from the data. (default: False)
  --sentences           For keeping sentences together, e.g., when reading
                        preformatted text. (default: False)
  -c END_CHARS, --end_chars END_CHARS
                        The characters signifying the end of a sentence.
                        (default: .!?;:))
  -q QUOTE_CHARS, --quote_chars QUOTE_CHARS
                        The characters that represent quotes. (default: "'”’)
  --block_removal_start [BLOCK_REMOVAL_START [BLOCK_REMOVAL_START ...]]
                        The starting strings for blocks to remove (default:
                        None)
  --block_removal_end [BLOCK_REMOVAL_END [BLOCK_REMOVAL_END ...]]
                        The ending strings for blocks to remove (default:
                        None)
  -m MAX_SENTENCES, --max_sentences MAX_SENTENCES
                        The maximum number of sentences per line. (default: 1)
```
