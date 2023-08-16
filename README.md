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
| pretrain | [Parquet](https://arrow.apache.org/docs/python/parquet.html) | Y | Y | N |    


## Compression formats

In case a format supports compression, then the following compression formats 
are automatically supported for loading/saving files:

* [bzip2](https://en.wikipedia.org/wiki/Bzip2): `.bz2`
* [gzip](https://en.wikipedia.org/wiki/Gzip): `.gz`
* [xz](https://en.wikipedia.org/wiki/XZ_Utils): `.xz`
* [zstd](https://en.wikipedia.org/wiki/Zstd): `.zst`, `.zstd`


## Tools

```
usage: llm-convert [-h|--help|--help-all] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-c]
                   reader
                   [filter [filter [...]]]
                   writer

Tool for converting between large language model (LLM) dataset formats.

readers:
   from-alpaca, from-csv-pairs, from-jsonlines-pairs, 
   from-parquet-pairs, from-parquet-pretrain
filters:
   keyword-pairs, pairs-to-pretrain
writers:
   to-alpaca, to-csv-pairs, to-jsonlines-pairs, to-parquet-pairs, 
   to-parquet-pretrain

optional arguments:
  -h, --help            show basic help message and exit
  --help-all            show basic help message plus help on all plugins and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -c, --compression     {None|bz2|gz|xz|zstd}
                        the type of compression to use when only providing an output
                        directory to the writer (default: None)
```

```
usage: llm-hf-download [-h] -i REPO_ID [-t {None,model,dataset,space}]
                       [-f FILENAME] [-r REVISION] [-o OUTPUT_DIR]
                       [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]

Tool for downloading files or datasets from huggingface for local conversion.

optional arguments:
  -h, --help            show this help message and exit
  -i REPO_ID, --repo_id REPO_ID
                        The name of the huggingface repository/dataset to
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
                        default huggingface cache directory when omitted.
                        (default: None)
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: INFO)
```


## Conversion plugins

```
from-alpaca
===========
domain(s): pairs
generates: PairData

usage: from-alpaca [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i INPUT
                   [INPUT ...]

Reads prompt/output pairs in Alpaca-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the Alpaca file(s) to read; global syntax is
                        supported (default: None)

from-csv-pairs
==============
domain(s): pairs
generates: PairData

usage: from-csv-pairs [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i INPUT
                      [INPUT ...] [--col_instruction COL] [--col_input COL]
                      [--col_output COL]

Reads prompt/output pairs in CSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the CSV file(s) to read; global syntax is
                        supported (default: None)
  --col_instruction COL
                        The name of the column with the instructions (default:
                        None)
  --col_input COL       The name of the column with the inputs (default: None)
  --col_output COL      The name of the column with the outputs (default:
                        None)

from-jsonlines-pairs
====================
domain(s): pairs
generates: PairData

usage: from-jsonlines-pairs [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i
                            INPUT [INPUT ...] [--att_instruction COL]
                            [--att_input COL] [--att_output COL]

Reads prompt/output pairs in JsonLines-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the JsonLines file(s) to read; global syntax
                        is supported (default: None)
  --att_instruction COL
                        The attribute with the instructions (default: None)
  --att_input COL       The attribute with the inputs (default: None)
  --att_output COL      The attribute with the outputs (default: None)

from-parquet-pairs
==================
domain(s): pairs
generates: PairData

usage: from-parquet-pairs [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i INPUT
                          [INPUT ...] [--col_instruction COL]
                          [--col_input COL] [--col_output COL]

Reads prompt/output pairs from Parquet database files.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the parquet file(s) to read; global syntax is
                        supported (default: None)
  --col_instruction COL
                        The name of the column with the instructions (default:
                        None)
  --col_input COL       The name of the column with the inputs (default: None)
  --col_output COL      The name of the column with the outputs (default:
                        None)

from-parquet-pretrain
=====================
domain(s): pretrain
generates: PretrainData

usage: from-parquet-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i
                             INPUT [INPUT ...] [--col_content COL]

Reads text from Parquet database files to use for pretraining.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to the parquet file(s) to read; global syntax is
                        supported (default: None)
  --col_content COL     The name of the column with the text to retrieve
                        (default: None)

keyword-pairs
=============
domain(s): pairs
accepts: PairData
generates: PairData

usage: keyword-pairs [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -k KEYWORD
                     [KEYWORD ...] [-L {any,instruction,input,output}]
                     [-a {keep,discard}]

Keeps or discards data records based on keyword(s).

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -k KEYWORD [KEYWORD ...], --keyword KEYWORD [KEYWORD ...]
                        The keywords to look for (default: None)
  -L {any,instruction,input,output}, --location {any,instruction,input,output}
                        Where to look for the keywords (default: any)
  -a {keep,discard}, --action {keep,discard}
                        How to react when a keyword is encountered (default:
                        keep)

pairs-to-pretrain
=================
domain(s): pairs, pretrain
accepts: PairData
generates: PretrainData

usage: pairs-to-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                         [-f {instruction,input,output} [{instruction,input,output} ...]]

Converts records of prompt/output pairs to pretrain ones.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -f {instruction,input,output} [{instruction,input,output} ...], --data_fields {instruction,input,output} [{instruction,input,output} ...]
                        The data fields to use for the pretrain content
                        (default: None)

to-alpaca
=========
domain(s): pairs
accepts: PairData

usage: to-alpaca [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o OUTPUT

Writes prompt/output pairs in Alpaca-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the Alpaca file to write (directory when
                        processing multiple files) (default: None)

to-csv-pairs
============
domain(s): pairs
accepts: PairData

usage: to-csv-pairs [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o OUTPUT
                    [--col_instruction COL] [--col_input COL]
                    [--col_output COL]

Writes prompt/output pairs in CSV format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the CSV file to write (directory when
                        processing multiple files) (default: None)
  --col_instruction COL
                        The name of the column for the instructions (default:
                        instruction)
  --col_input COL       The name of the column for the inputs (default: input)
  --col_output COL      The name of the column for the outputs (default:
                        output)

to-jsonlines-pairs
==================
domain(s): pairs
accepts: PairData

usage: to-jsonlines-pairs [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o OUTPUT
                          [--att_instruction COL] [--att_input COL]
                          [--att_output COL]

Writes prompt/output pairs in JsonLines-like JSON format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the JsonLines file to write (directory when
                        processing multiple files) (default: None)
  --att_instruction COL
                        The attribute for the instructions (default: None)
  --att_input COL       The attribute for the inputs (default: None)
  --att_output COL      The attribute for the outputs (default: None)

to-parquet-pairs
================
domain(s): pairs
accepts: PairData

usage: to-parquet-pairs [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o OUTPUT
                        [--col_instruction COL] [--col_input COL]
                        [--col_output COL]

Writes prompt/output pairs in Parquet database format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the CSV file to write (directory when
                        processing multiple files) (default: None)
  --col_instruction COL
                        The name of the column for the instructions (default:
                        None)
  --col_input COL       The name of the column for the inputs (default: None)
  --col_output COL      The name of the column for the outputs (default: None)

to-parquet-pretrain
===================
domain(s): pretrain
accepts: PretrainData

usage: to-parquet-pretrain [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -o
                           OUTPUT [--col_content COL]

Writes text used for pretraining in Parquet database format.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -o OUTPUT, --output OUTPUT
                        Path of the CSV file to write (directory when
                        processing multiple files) (default: None)
  --col_content COL     The name of the column for the text content (default:
                        None)
```
