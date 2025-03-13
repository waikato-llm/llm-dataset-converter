# inspect

* domain(s): any
* accepts: seppl.AnyData
* generates: seppl.AnyData

Allows inspecting the data flowing through the pipeline.

```
usage: inspect [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-N LOGGER_NAME]
               [-m {interactive,non-interactive}]
               [-o {stdout,stderr,logger,file}] [--output_file OUTPUT_FILE]
               [-L [{any,instruction,input,output,content,text} ...]]
               [-g [LANGUAGE ...]] [-k [KEY ...]]

Allows inspecting the data flowing through the pipeline.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -m {interactive,non-interactive}, --mode {interactive,non-interactive}
                        The mode to operate in. (default: interactive)
  -o {stdout,stderr,logger,file}, --output {stdout,stderr,logger,file}
                        How to output the data. (default: stdout)
  --output_file OUTPUT_FILE
                        The file to store the data in, in case of output
                        'file'. Supported placeholders: {HOME}, {CWD}, {TMP}
                        (default: None)
  -L [{any,instruction,input,output,content,text} ...], --location [{any,instruction,input,output,content,text} ...]
                        Which textual data to output; classification:
                        any|text, pairs: any|instruction|input|output,
                        pretrain: any|content, translation: any|content
                        (default: None)
  -g [LANGUAGE ...], --language [LANGUAGE ...]
                        The language(s) to output (default: None)
  -k [KEY ...], --meta-data-key [KEY ...]
                        The meta-data value to output (default: None)
```
