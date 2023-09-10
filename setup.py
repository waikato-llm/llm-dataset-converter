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
            "llm-entry-points=ldc.entry_points:sys_main",
            "llm-help=ldc.help:sys_main",
            "llm-hf-download=ldc.huggingface.download:sys_main",
        ],
        "ldc.readers": [
            "from-csv-pt=ldc.pretrain:CsvPretrainReader",
            "from-jsonlines-pt=ldc.pretrain:JsonLinesPretrainReader",
            "from-parquet-pt=ldc.pretrain:ParquetPretrainReader",
            "from-tsv-pt=ldc.pretrain:TsvPretrainReader",
            "from-txt-pt=ldc.pretrain:TxtPretrainReader",
            "from-alpaca=ldc.supervised.pairs:AlpacaReader",
            "from-csv-pr=ldc.supervised.pairs:CsvPairsReader",
            "from-jsonlines-pr=ldc.supervised.pairs:JsonLinesPairReader",
            "from-parquet-pr=ldc.supervised.pairs:ParquetPairsReader",
            "from-tsv-pr=ldc.supervised.pairs:TsvPairsReader",
            "from-csv-t9n=ldc.translation:CsvTranslationReader",
            "from-jsonlines-t9n=ldc.translation:JsonLinesTranslationReader",
            "from-parquet-t9n=ldc.translation:ParquetTranslationReader",
            "from-tsv-t9n=ldc.translation:TsvTranslationReader",
            "from-txt-t9n=ldc.translation:TxtTranslationReader"
        ],
        "ldc.filters": [
            "change-case=ldc.filter:ChangeCase",
            "keyword=ldc.filter:Keyword",
            "metadata=ldc.filter:MetaData",
            "multi-filter=ldc.filter:MultiFilter",
            "pairs-to-pretrain=ldc.filter:PairsToPretrain",
            "reset-ids=ldc.filter:ResetIDs",
            "skip-duplicate-ids=ldc.filter:SkipDuplicateIDs",
            "skip-duplicate-text=ldc.filter:SkipDuplicateText",
            "split=ldc.filter:Split",
            "text-length=ldc.filter:TextLength",
            "translation-to-pretrain=ldc.filter:TranslationToPretrain",
            "pretrain-sentences=ldc.pretrain:PretrainSentences",
            "language=ldc.translation:Language",
            "require-languages=ldc.translation:RequireLanguages"
        ],
        "ldc.writers": [
            "to-csv-pt=ldc.pretrain:CsvPretrainWriter",
            "to-jsonlines-pt=ldc.pretrain:JsonLinesPretrainWriter",
            "to-parquet-pt=ldc.pretrain:ParquetPretrainWriter",
            "to-tsv-pt=ldc.pretrain:TsvPretrainWriter",
            "to-txt-pt=ldc.pretrain:TxtPretrainWriter",
            "to-alpaca=ldc.supervised.pairs:AlpacaWriter",
            "to-csv-pr=ldc.supervised.pairs:CsvPairsWriter",
            "to-jsonlines-pr=ldc.supervised.pairs:JsonLinesPairWriter",
            "to-parquet-pr=ldc.supervised.pairs:ParquetPairsWriter",
            "to-tsv-pr=ldc.supervised.pairs:TsvPairsWriter",
            "to-csv-t9n=ldc.translation:CsvTranslationWriter",
            "to-jsonlines-t9n=ldc.translation:JsonLinesTranslationWriter",
            "to-parquet-t9n=ldc.translation:ParquetTranslationWriter",
            "to-tsv-t9n=ldc.translation:TsvTranslationWriter",
            "to-txt-t9n=ldc.translation:TxtTranslationWriter"
        ]
    },
)
