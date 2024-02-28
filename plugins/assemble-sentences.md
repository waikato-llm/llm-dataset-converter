# assemble-sentences

* domain(s): pairs, pretrain, translation, classification
* accepts: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData
* generates: ldc.api.supervised.pairs.PairData, ldc.api.pretrain.PretrainData, ldc.api.translation.TranslationData, ldc.api.supervised.classification.ClassificationData

For keeping sentences together, e.g., when reading preformatted text.

```
usage: assemble-sentences [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                          [-N LOGGER_NAME] [-c END_CHARS] [-q QUOTE_CHARS]
                          [-m MAX_SENTENCES]
                          [-L [{any,instruction,input,output,content,text} [{any,instruction,input,output,content,text} ...]]]
                          [-g [LANGUAGE [LANGUAGE ...]]]

For keeping sentences together, e.g., when reading preformatted text.

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
  -L [{any,instruction,input,output,content,text} [{any,instruction,input,output,content,text} ...]], --location [{any,instruction,input,output,content,text} [{any,instruction,input,output,content,text} ...]]
                        Where to assemble the sentences; classification:
                        any|text, pairs: any|instruction|input|output,
                        pretrain: any|content, translation: any|content
                        (default: any)
  -g [LANGUAGE [LANGUAGE ...]], --language [LANGUAGE [LANGUAGE ...]]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```
