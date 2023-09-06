# llm-dataset-converter
For converting large language model (LLM) datasets from one format into another.


## Installation

```bash
pip install git+https://github.com/waikato-datamining/llm-dataset-converter.git
```


## Datasets

The following repository contains a curated list of datasets for LLMs:

https://github.com/Zjh-819/LLMDataHub


## Dataset formats

The following dataset formats are supported:

| Domain      | Format | Read  | Write | Compression |
| :---        | :---   | :---  | :---  | :---:       |
| pairs       | [Alpaca](https://github.com/tatsu-lab/stanford_alpaca#data-release)  | [from-alpaca](plugins/from-alpaca.md) | [to-alpaca](plugins/to-alpaca.md) | Y |    
| pairs       | CSV | [from-csv-pr](plugins/from-csv-pr.md) | [to-csv-pr](plugins/to-csv-pr.md) | Y |
| pairs       | [Jsonlines](https://jsonlines.org/) | [from-jsonlines-pr](plugins/from-jsonlines-pr.md) | [to-jsonlines-pr](plugins/to-jsonlines-pr.md) | Y |
| pairs       | [Parquet](https://arrow.apache.org/docs/python/parquet.html) | [from-parquet-pr](plugins/from-parquet-pr.md) | [to-parquet-pr](plugins/to-parquet-pr.md) | N |    
| pairs       | TSV | [from-tsv-pr](plugins/from-tsv-pr.md) | [to-tsv-pr](plugins/to-tsv-pr.md) | Y |
| pretrain    | CSV | [from-csv-pt](plugins/from-csv-pt.md) | [to-csv-pt](plugins/to-csv-pt.md) | Y |
| pretrain    | [Jsonlines](https://jsonlines.org/) | [from-jsonlines-pt](plugins/from-jsonlines-pt.md) | [to-jsonlines-pt](plugins/to-jsonlines-pt.md) | Y |
| pretrain    | [Parquet](https://arrow.apache.org/docs/python/parquet.html) | [from-parquet-pt](plugins/from-parquet-pt.md) | [to-parquet-pt](plugins/to-parquet-pt.md) | N |    
| pretrain    | TSV | [from-tsv-pt](plugins/from-tsv-pt.md) | [to-tsv-pt](plugins/to-tsv-pt.md) | Y |
| pretrain    | TXT | [from-txt-pt](plugins/from-txt-pt.md) | [to-txt-pt](plugins/to-txt-pt.md) | Y <sup>1</sup> |
| translation | CSV | [from-csv-t9n](plugins/from-csv-t9n.md) | [to-csv-t9n](plugins/to-csv-t9n.md) | Y |
| translation | [Jsonlines](https://jsonlines.org/) <sup>2</sup> | [from-jsonlines-t9n](plugins/from-jsonlines-t9n.md) | [to-jsonlines-t9n](plugins/to-jsonlines-t9n.md) | Y |
| translation | TSV | [from-tsv-t9n](plugins/from-tsv-t9n.md) | [to-tsv-t9n](plugins/to-tsv-t9n.md) | Y |
| translation | TXT | [from-txt-t9n](plugins/from-txt-t9n.md) | [to-txt-t9n](plugins/to-txt-t9n.md) | Y <sup>1</sup> |

<sup>1</sup> Not available when concatenating content in single file.
<sup>2</sup> Format defined here: https://github.com/huggingface/transformers/blob/main/examples/pytorch/translation/README.md

## Compression formats

In case a format supports compression, then the following compression formats 
are automatically supported for loading/saving files:

* [bzip2](https://en.wikipedia.org/wiki/Bzip2): `.bz2`
* [gzip](https://en.wikipedia.org/wiki/Gzip): `.gz`
* [xz](https://en.wikipedia.org/wiki/XZ_Utils): `.xz`
* [zstd](https://en.wikipedia.org/wiki/Zstd): `.zst`, `.zstd`


## Tools

Dataset conversion:

```
usage: llm-convert [-h|--help|--help-all|-help-plugin NAME]
                   [-c {None,bz2,gz,xz,zstd}]
                   [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                   reader
                   [filter [filter [...]]]
                   writer

Tool for converting between large language model (LLM) dataset formats.

readers:
   from-alpaca, from-csv-pr, from-csv-pt, from-jsonlines-pr, 
   from-jsonlines-pt, from-parquet-pr, from-parquet-pt
filters:
   keyword-pr, pairs-to-pt
writers:
   to-alpaca, to-csv-pr, to-csv-pt, to-jsonlines-pr, 
   to-jsonlines-pt, to-parquet-pr, to-parquet-pt

optional arguments:
  -h, --help            show basic help message and exit
  --help-all            show basic help message plus help on all plugins and exit
  --help-plugin NAME    show help message for plugin NAME and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        the logging level to use (default: WARN)
  -c {None,bz2,gz,xz,zstd}, --compression {None,bz2,gz,xz,zstd}
                        the type of compression to use when only providing an output
                        directory to the writer (default: None)
```

Download tool for [Hugging Face](https://huggingface.co/) datasets/files:

```
usage: llm-hf-download [-h] -i REPO_ID [-t {None,model,dataset,space}]
                       [-f [FILENAME [FILENAME ...]]] [-r REVISION]
                       [-o OUTPUT_DIR] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]

Tool for downloading files or datasets from Hugging Face
(https://huggingface.co/) for local conversion.

optional arguments:
  -h, --help            show this help message and exit
  -i REPO_ID, --repo_id REPO_ID
                        The name of the Hugging Face repository/dataset to
                        download (default: None)
  -t {None,model,dataset,space}, --repo_type {None,model,dataset,space}
                        The type of the repository (default: None)
  -f [FILENAME [FILENAME ...]], --filename [FILENAME [FILENAME ...]]
                        The name of the file to download rather than the full
                        dataset (default: None)
  -r REVISION, --revision REVISION
                        The revision of the dataset to download, omit for
                        latest (default: None)
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        The directory to store the data in, stores it in the
                        default Hugging Face cache directory when omitted.
                        (default: None)
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: INFO)
```

Tool for generating help screens for plugins:

```
usage: llm-help [-h] [-p NAME] [-f FORMAT] [-L INT] [-o PATH]
                [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]

Tool for outputting help for plugins in various formats.

optional arguments:
  -h, --help            show this help message and exit
  -p NAME, --plugin_name NAME
                        The name of the plugin to generate the help for,
                        generates it for all if not specified (default: None)
  -f FORMAT, --help_format FORMAT
                        The output format to generate (default: text)
  -L INT, --heading_level INT
                        The level to use for the heading (default: 1)
  -o PATH, --output PATH
                        The directory or file to store the help in; outputs it
                        to stdout if not supplied; if pointing to a directory,
                        automatically generates file name from plugin name and
                        help format (default: None)
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
```

Tool for generating the `entry_points` section for readers, filters and writers:

```
usage: llm-entry-points [-h] [-m [PACKAGE [PACKAGE ...]]]
                        [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]

Tool generating data for the 'entry_points' section in setup.py, populating it
with the readers, filters and writers.

optional arguments:
  -h, --help            show this help message and exit
  -m [PACKAGE [PACKAGE ...]], --modules [PACKAGE [PACKAGE ...]]
                        The names of the module packages, uses the default
                        ones if not provided. (default: None)
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
```


## Other plugins

Filters:  
* [keyword](plugins/keyword.md)
* [language](plugins/language.md)
* [metadata](plugins/metadata.md)
* [multi-filter](plugins/multi-filter.md)
* [pairs-to-pretrain](plugins/pairs-to-pretrain.md)
* [skip-duplicate-ids](plugins/skip-duplicate-ids.md)
* [skip-duplicate-text](plugins/skip-duplicate-text.md)
* [split](plugins/split.md)
* [text-length](plugins/text-length.md)
* [translation-to-pretrain](plugins/translation-to-pretrain.md)


## Command-line examples

Use the [alpaca_data_cleaned.json](https://github.com/gururise/AlpacaDataCleaned/blob/main/alpaca_data_cleaned.json)
dataset for the following examples.

### Conversion

```bash
llm-convert \
  from-alpaca \
    --input ./alpaca_data_cleaned.json \
  to-csv-pr \
    --output alpaca_data_cleaned.csv
```

If you want some logging output, e.g., on progress and what files are being 
processed/generated:

```bash
llm-convert \
  -l INFO \
  from-alpaca \
    --input ./alpaca_data_cleaned.json \
    -l INFO \
  to-csv-pr \
    --output alpaca_data_cleaned.csv
    -l INFO
```

### Compression

The output gets automatically compressed (when the format supports that), based
on the extension that you use for the output.

The following uses Gzip to compress the CSV file:

```bash
llm-convert \
  from-alpaca \
    --input ./alpaca_data_cleaned.json \
  to-csv-pr \
    --output alpaca_data_cleaned.csv.gz
```

The input gets automatically decompressed based on its extension, provided 
the format supports that.

### Processing multiple files

Provided that the reader supports, you can also process multiple files, one
after the other. For that you either specify them explicitly (multiple 
arguments to the `--input` option) or use a glob syntax (e.g., `--input "*.json"`).
For the latter, you should surround the argument with double quotes to avoid
the shell expanding the names automatically.

As for specifying the output, you simply specify the output directory. An output
file name gets automatically generated from the name of the current input file
that is being processed.

If you want to compress the output files, you need to specify your preferred
compression format via the global `-c/--compression` option of the `llm-convert`
tool. By default, no compression is used.

### Filtering

Instead of just reading and writing the data records, you can also inject
filters in between them. E.g., the following command-line will load the
Alpaca JSON dataset and only keep records that have the keyword `function`
in either the `instruction`, `input` or `output` data of the record:

```bash
llm-convert \
  -l INFO \
  from-alpaca \
    -l INFO \
    --input alpaca_data_cleaned.json \
  keyword \
    -l INFO \
    --keyword function \
    --location any \
    --action keep \
  to-alpaca \
    -l INFO \
    --output alpaca_data_cleaned-filtered.json 
```

**NB:** When chaining filters, the tool checks whether accepted input and 
generated output is compatible (including from reader/writer).

### Download

The following command downloads the file `vocab.json` from the Hugging Face
project [lysandre/arxiv-nlp](https://huggingface.co/lysandre/arxiv-nlp):

```bash
llm-hf-download \
  -l INFO \
  -i lysandre/arxiv-nlp \
  -f vocab.json \
  -o .
```

The next command gets the file `part_1_200000.parquet` from the dataset
[nampdn-ai/tiny-codes](https://huggingface.co/datasets/nampdn-ai/tiny-codes) 
(if you don't specify a filename, the complete dataset will get downloaded):

```bash
llm-hf-download \
  -l INFO \
  -i nampdn-ai/tiny-codes \
  -t dataset \
  -f part_1_200000.parquet \
  -o .
```

**NB:** Hugging Face will cache files locally in your home directory before
copying it to the location that you specified.


## Code example

Of course, you can use the library also from Python itself.

The following code sets up a pipeline that reads in a prompt/response 
dataset in Alpaca format, filters out records that do not contain the 
keyword `function` anywhere in the record, converts it to *pretrain* data
and then outputs it in zstandard-compressed jsonlines format:

```python
from ldc.core import Session, LOGGING_INFO, init_logging
from ldc.io import COMPRESSION_ZSTD
from ldc.registry import register_plugins
from ldc.supervised.pairs import AlpacaReader, PAIRDATA_FIELDS
from ldc.pretrain import JsonLinesPretrainWriter
from ldc.filter import PairsToPretrain, Keyword
from ldc.execution import execute

init_logging()
register_plugins()

execute(
    AlpacaReader(
        source="./alpaca_data_cleaned.json",
        logging_level=LOGGING_INFO
    ),
    [
        Keyword(
            keywords=["function"],
            logging_level=LOGGING_INFO
        ),
        PairsToPretrain(
            data_fields=PAIRDATA_FIELDS
        ),
    ],
    JsonLinesPretrainWriter(
        target="./output",
        att_content="text",
        logging_level=LOGGING_INFO
    ),
    Session()
        .set_logging_level(LOGGING_INFO)
        .set_compression(COMPRESSION_ZSTD),
)
```
