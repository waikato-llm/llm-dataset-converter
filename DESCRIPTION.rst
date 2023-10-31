The **llm-dataset-converter** allows the conversion between
various dataset formats for large language models (LLMs).
Filters can be supplied as well, e.g., for cleaning up the data.

Dataset formats:

- pairs: alpaca (r/w), csv (r/w), jsonl (r/w), parquet (r/w), tsv (r/w)
- pretrain: csv (r/w), jsonl (r/w), parquet (r/w), tsv (r/w), txt (r/w)
- translation: csv (r/w), jsonl (r/w), parquet (r/w), tsv (r/w), txt (r/w)


Compression formats:

- bzip
- gzip
- xz
- zstd


Examples:

Simple conversion with logging info::

    llm-convert \
      from-alpaca \
        -l INFO \
        --input ./alpaca_data_cleaned.json \
      to-csv-pr \
        -l INFO \
        --output alpaca_data_cleaned.csv

Automatic decompression/compression (based on file extension)::

    llm-convert \
      from-alpaca \
        --input ./alpaca_data_cleaned.json.xz \
      to-csv-pr \
        --output alpaca_data_cleaned.csv.gz

Filtering::

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


