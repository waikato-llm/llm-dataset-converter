from setuptools import setup


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
    packages=[
        "ldc",
        "ldc.filter",
        "ldc.huggingface",
        "ldc.pretrain",
        "ldc.supervised.context",
        "ldc.supervised.dialog",
        "ldc.supervised.pairs",
    ],
    install_requires=[
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
            # pretrain
            "from-csv-pretrain=ldc.pretrain:CsvPretrainReader",
            "from-jsonlines-pretrain=ldc.pretrain:JsonLinesPretrainReader",
            "from-parquet-pretrain=ldc.pretrain:ParquetPretrainReader",
        ],
        "ldc.filters": [
            "keyword-pairs=ldc.supervised.pairs:Keyword",
            "pairs-to-pretrain=ldc.filter:PairsToPretrain",
        ],
        "ldc.writers": [
            # pairs
            "to-alpaca=ldc.supervised.pairs:AlpacaWriter",
            "to-csv-pairs=ldc.supervised.pairs:CsvPairsWriter",
            "to-jsonlines-pairs=ldc.supervised.pairs:JsonLinesPairWriter",
            "to-parquet-pairs=ldc.supervised.pairs:ParquetPairsWriter",
            # pretrain
            "to-csv-pretrain=ldc.pretrain:CsvPretrainWriter",
            "to-jsonlines-pretrain=ldc.pretrain:JsonLinesPretrainWriter",
            "to-parquet-pretrain=ldc.pretrain:ParquetPretrainWriter",
        ],
    },
)
