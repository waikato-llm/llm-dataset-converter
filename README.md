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

| Domain   | Format | Read  | Write | Compression |
| :---     | :---   | :---: | :---: | :---:       |
| pairs    | [Alpaca](https://github.com/tatsu-lab/stanford_alpaca#data-release)  | Y | Y | Y |    
| pairs    | CSV | Y | Y | Y |
| pairs    | [Jsonlines](https://jsonlines.org/) | Y | Y | Y |
| pairs    | [Parquet](https://arrow.apache.org/docs/python/parquet.html) | Y | Y | N |    
| pretrain | CSV | Y | Y | Y |
| pretrain | [Jsonlines](https://jsonlines.org/) | Y | Y | Y |
| pretrain | [Parquet](https://arrow.apache.org/docs/python/parquet.html) | Y | Y | N |    


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
   from-alpaca, from-csv-pairs, from-csv-pretrain, from-jsonlines-pairs, 
   from-jsonlines-pretrain, from-parquet-pairs, from-parquet-pretrain
filters:
   keyword-pairs, pairs-to-pretrain
writers:
   to-alpaca, to-csv-pairs, to-csv-pretrain, to-jsonlines-pairs, 
   to-jsonlines-pretrain, to-parquet-pairs, to-parquet-pretrain

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
                       [-f FILENAME] [-r REVISION] [-o OUTPUT_DIR]
                       [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]

Tool for downloading files or datasets from Hugging Face
(https://huggingface.co/) for local conversion.

optional arguments:
  -h, --help            show this help message and exit
  -i REPO_ID, --repo_id REPO_ID
                        The name of the Hugging Face repository/dataset to
                        download (default: None)
  -t {None,model,dataset,space}, --repo_type {None,model,dataset,space}
                        The type of the repository (default: None)
  -f FILENAME, --filename FILENAME
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
usage: llm-help [-h] -p NAME [-f FORMAT] [-l INT] [-o FILE]

Tool for outputting help for plugins in various formats.

optional arguments:
  -h, --help            show this help message and exit
  -p NAME, --plugin_name NAME
                        The name of the plugin to generate the help for
                        (default: None)
  -f FORMAT, --help_format FORMAT
                        The output format to generate (default: text)
  -l INT, --heading_level INT
                        The level to use for the heading (default: 1)
  -o FILE, --output FILE
                        The file to store the help in, outputs it to stdout if
                        not supplied (default: None)
```


## Plugins

Readers:
* [from-alpaca](plugins/from-alpaca.md)
* [from-csv-pairs](plugins/from-csv-pairs.md)
* [from-csv-pretrain](plugins/from-csv-pretrain.md)
* [from-jsonlines-pairs](plugins/from-jsonlines-pairs.md)
* [from-jsonlines-pretrain](plugins/from-jsonlines-pretrain.md)
* [from-parquet-pairs](plugins/from-parquet-pairs.md)
* [from-parquet-pretrain](plugins/from-parquet-pretrain.md)

Filters:  
* [keyword-pairs](plugins/keyword-pairs.md)
* [pairs-to-pretrain](plugins/pairs-to-pretrain.md)
  
Writers:
* [to-alpaca](plugins/to-alpaca.md)
* [to-csv-pairs](plugins/to-csv-pairs.md)
* [to-csv-pretrain](plugins/to-csv-pretrain.md)
* [to-jsonlines-pairs](plugins/to-jsonlines-pairs.md)
* [to-jsonlines-pretrain](plugins/to-jsonlines-pretrain.md)
* [to-parquet-pairs](plugins/to-parquet-pairs.md)
* [to-parquet-pretrain](plugins/to-parquet-pretrain.md)


## Examples

Use the [alpaca_data_cleaned.json](https://github.com/gururise/AlpacaDataCleaned/blob/main/alpaca_data_cleaned.json)
dataset for the following examples.

### Conversion

```bash
llm-convert \
  from-alpaca \
    --input ./alpaca_data_cleaned.json \
  to-csv-pairs \
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
  to-csv-pairs \
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
  to-csv-pairs \
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
  keyword-pairs \
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
