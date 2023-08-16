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
usage: llm-convert [-h|--help|--help-all] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-c]
                   reader
                   [filter [filter [...]]]
                   writer

Tool for converting between large language model (LLM) dataset formats.

readers:
   from-alpaca, from-csv-pairs, from-jsonlines-pairs, 
   from-parquet-pairs, from-csv-pretrain, from-jsonlines-pretrain, 
   from-parquet-pretrain
filters:
   keyword-pairs, pairs-to-pretrain
writers:
   to-alpaca, to-csv-pairs, to-jsonlines-pairs, to-parquet-pairs, 
   to-csv-pretrain, to-jsonlines-pretrain, to-parquet-pretrain

optional arguments:
  -h, --help            show basic help message and exit
  --help-all            show basic help message plus help on all plugins and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
  -c, --compression     {None|bz2|gz|xz|zstd}
                        the type of compression to use when only providing an output
                        directory to the writer (default: None)
```

Download tool for [huggingface](https://huggingface.co/) datasets/files:

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
