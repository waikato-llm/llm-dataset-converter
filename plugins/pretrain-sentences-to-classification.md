# pretrain-sentences-to-classification

* domain(s): classification, pretrain
* accepts: ldc.api.pretrain.PretrainData
* generates: ldc.api.supervised.classification.ClassificationData

Converts sentences from pretrain records to text classification ones by using X sentences as text and the specified label. Can be used to generate classification datasets from just pretrain data.

```
usage: pretrain-sentences-to-classification [-h]
                                            [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                                            [-N LOGGER_NAME] [-c END_CHARS]
                                            [-r NUM_SENTENCES_TEXT] [-L LABEL]

Converts sentences from pretrain records to text classification ones by using
X sentences as text and the specified label. Can be used to generate
classification datasets from just pretrain data.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -c END_CHARS, --end_chars END_CHARS
                        The characters signifying the end of a sentence.
                        (default: .!?;:))
  -r NUM_SENTENCES_TEXT, --num_sentences_text NUM_SENTENCES_TEXT
                        The number of sentences following the prompt sentence
                        to use as response. (default: 5)
  -L LABEL, --label LABEL
                        The label to use. (default: None)
```
