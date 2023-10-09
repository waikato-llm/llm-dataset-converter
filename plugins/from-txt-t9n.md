# from-txt-t9n

* domain(s): translation
* generates: ldc.translation.TranslationData

Reads translation data from plain text files, with each line representing a record for one specific language.

```
usage: from-txt-t9n [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                    [-N LOGGER_NAME] -i INPUT [INPUT ...] [--col_id COL]
                    [--col_lang COL] --col_content COL [--col_sep COL_SEP]
                    [--lang_in_id] [--expr_lang EXPR_LANG] [--expr_id EXPR_ID]

Reads translation data from plain text files, with each line representing a
record for one specific language.

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
  --col_id COL          The 1-based index of the column with the row IDs (gets
                        stored under 'id' in meta-data) (default: None)
  --col_lang COL        The 1-based of the column with the language ID
                        (default: None)
  --col_content COL     The 1-based of the column with the text content
                        (default: None)
  --col_sep COL_SEP     Separator between data columns, use {TAB}. (default:
                        :)
  --lang_in_id          Whether the language is part in the ID column.
                        (default: False)
  --expr_lang EXPR_LANG
                        The regular expression for parsing the ID column and
                        extracting the language as first group of the
                        expression (only if --lang_in_id). (default:
                        ([a-z][a-z]).*)
  --expr_id EXPR_ID     The regular expression for parsing the ID column and
                        extracting the actual ID as first group of the
                        expression (only if --lang_in_id). (default:
                        [a-z][a-z]-(.*))
```
