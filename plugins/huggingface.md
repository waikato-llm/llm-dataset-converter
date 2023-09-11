# huggingface

For downloading files and datasets from Huggingface (https://huggingface.co/).

```
usage: huggingface [-h] [-l {DEBUG,INFO,WARN,ERROR,CRITICAL}] -i REPO_ID
                   [-t {None,model,dataset,space}]
                   [-f [FILENAME [FILENAME ...]]] [-r REVISION]
                   [-o OUTPUT_DIR]

For downloading files and datasets from Huggingface (https://huggingface.co/).

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARN,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        The logging level to use (default: WARN)
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
```
