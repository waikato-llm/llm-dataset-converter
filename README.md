# llm-dataset-converter
For converting large language model (LLM) datasets from one format into another.

## Installation

```bash
pip install git+https://github.com/waikato-datamining/llm-dataset-converter.git
```


## Data formats

| Domain | Format | Read  | Write |
| :---   | :---   | :---: | :---: |
| pairs  | [Alpaca](https://github.com/tatsu-lab/stanford_alpaca#data-release)  | Y | Y |    
| pairs  | CSV | Y | Y |    
| pairs  | [Parquet](https://arrow.apache.org/docs/python/parquet.html) | Y | Y |    


## Compression formats

The following compression formats are automatically supported for loading/saving
files:

* [bzip2](https://en.wikipedia.org/wiki/Bzip2): `.bz2`
* [gzip](https://en.wikipedia.org/wiki/Gzip): `.gz`
* [xz](https://en.wikipedia.org/wiki/XZ_Utils): `.xz`
* [zstd](https://en.wikipedia.org/wiki/Zstd): `.zst`, `.zstd`


## Tools

```
usage: llm-convert [-h] [-v]
                   {from-alpaca|from-csv-pairs}
                   [pairs-keyword, ...]
                   {to-alpaca|to-csv-pairs}

Tool for converting between large language model (LLM) dataset formats.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Whether to be more verbose with the output (default: False)
```

```
usage: llm-hf-download [-h] -i REPO_ID [-t {None,model,dataset,space}]
                       [-f FILENAME] [-r REVISION] [-o OUTPUT_DIR] [-v]

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
  -v, --verbose         Whether to be more verbose with the output (default:
                        False)
```


## Datasets

The following repository contains a curated list of datasets for LLMs:

https://github.com/Zjh-819/LLMDataHub
