# change-case

* domain(s): pairs, pretrain, translation
* accepts: PairData, PretrainData, TranslationData
* generates: PairData, PretrainData, TranslationData

Changes the case of text, e.g., to all lower case.

```
usage: change-case [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                   [-c {unchanged,lower,upper,title}]
                   [-L {any,instruction,input,output,content}]
                   [-g [LANGUAGE [LANGUAGE ...]]]

Changes the case of text, e.g., to all lower case.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -c {unchanged,lower,upper,title}, --case {unchanged,lower,upper,title}
                        How to change the case of the text (default: lower)
  -L {any,instruction,input,output,content}, --location {any,instruction,input,output,content}
                        Where to look for the keywords; pairs:
                        any,instruction,input,output, pretrain: any,content,
                        translation: any,content (default: any)
  -g [LANGUAGE [LANGUAGE ...]], --language [LANGUAGE [LANGUAGE ...]]
                        The languages to inspect; inspects all if not
                        specified (default: None)
```