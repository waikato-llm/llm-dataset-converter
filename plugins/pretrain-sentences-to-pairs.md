# pretrain-sentences-to-pairs

* domain(s): pairs, pretrain
* accepts: ldc.api.pretrain.PretrainData
* generates: ldc.api.supervised.pairs.PairData

Converts sentences from pretrain records to prompt/response pairs by using one sentence as the prompt and the following X sentences as response. Can be used to generate artificial prompt/response datasets from just pretrain data.

```
usage: pretrain-sentences-to-pairs [-h]
                                   [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                                   [-N LOGGER_NAME] [-c END_CHARS]
                                   [-p PROMPT_STEP]
                                   [-r NUM_SENTENCES_RESPONSE]

Converts sentences from pretrain records to prompt/response pairs by using one
sentence as the prompt and the following X sentences as response. Can be used
to generate artificial prompt/response datasets from just pretrain data.

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
  -p PROMPT_STEP, --prompt_step PROMPT_STEP
                        The step size for selecting sentences as prompt; no
                        sentence will be used for prompt if 0. (default: 1)
  -r NUM_SENTENCES_RESPONSE, --num_sentences_response NUM_SENTENCES_RESPONSE
                        The number of sentences following the prompt sentence
                        to use as response. (default: 5)
```
