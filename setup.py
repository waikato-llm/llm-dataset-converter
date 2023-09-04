from setuptools import setup, find_namespace_packages


def _read(f):
    """
    Reads in the content of the file.
    :param f: the file to read
    :type f: str
    :return: the content
    :rtype: str
    """
    return open(f, 'rb').read()


setup(
    name="llm-dataset-converter",
    description="Python3 library for converting between various LLM dataset formats.",
    long_description=(
        _read('DESCRIPTION.rst') + b'\n' +
        _read('CHANGES.rst')).decode('utf-8'),
    url="https://github.com/waikato-datamining/llm-dataset-converter",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3',
    ],
    license='MIT License',
    package_dir={
        '': 'src'
    },
    packages=find_namespace_packages(where='src'),
    install_requires=[
        "chardet",
        "pandas",
        "jsonlines",
        "pyarrow",
        "pyzstd",
        "huggingface-hub",
    ],
    version="0.0.1",
    author='Peter Reutemann',
    author_email='fracpete@waikato.ac.nz',
    entry_points={
        "console_scripts": [
            "llm-convert=ldc.convert:sys_main",
            "llm-help=ldc.help:sys_main",
            "llm-hf-download=ldc.huggingface.download:sys_main",
        ],
        "ldc.readers": [
            # pairs
            "from-alpaca=ldc.supervised.pairs:AlpacaReader",
            "from-csv-pairs=ldc.supervised.pairs:CsvPairsReader",
            "from-jsonlines-pairs=ldc.supervised.pairs:JsonLinesPairReader",
            "from-parquet-pairs=ldc.supervised.pairs:ParquetPairsReader",
            "from-tsv-pairs=ldc.supervised.pairs:TsvPairsReader",
            # pretrain
            "from-csv-pretrain=ldc.pretrain:CsvPretrainReader",
            "from-jsonlines-pretrain=ldc.pretrain:JsonLinesPretrainReader",
            "from-parquet-pretrain=ldc.pretrain:ParquetPretrainReader",
            "from-tsv-pretrain=ldc.pretrain:TsvPretrainReader",
            "from-txt-pretrain=ldc.pretrain:TxtPretrainReader",
        ],
        "ldc.filters": [
            "keyword=ldc.filter:Keyword",
            "pairs-to-pretrain=ldc.filter:PairsToPretrain",
            "skip-duplicate-ids=ldc.filter:SkipDuplicateIDs",
        ],
        "ldc.writers": [
            # pairs
            "to-alpaca=ldc.supervised.pairs:AlpacaWriter",
            "to-csv-pairs=ldc.supervised.pairs:CsvPairsWriter",
            "to-jsonlines-pairs=ldc.supervised.pairs:JsonLinesPairWriter",
            "to-parquet-pairs=ldc.supervised.pairs:ParquetPairsWriter",
            "to-tsv-pairs=ldc.supervised.pairs:TsvPairsWriter",
            # pretrain
            "to-csv-pretrain=ldc.pretrain:CsvPretrainWriter",
            "to-jsonlines-pretrain=ldc.pretrain:JsonLinesPretrainWriter",
            "to-parquet-pretrain=ldc.pretrain:ParquetPretrainWriter",
            "to-tsv-pretrain=ldc.pretrain:TsvPretrainWriter",
            "to-txt-pretrain=ldc.pretrain:TxtPretrainWriter",
        ],
    },
)
