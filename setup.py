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
    url="https://github.com/waikato-llm/llm-dataset-converter",
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
        "seppl>=0.1.3",
        "pyyaml",
        "wai.logging",
    ],
    version="0.2.0",
    author='Peter Reutemann',
    author_email='fracpete@waikato.ac.nz',
    entry_points={
        "console_scripts": [
            "llm-append=ldc.tool.append:sys_main",
            "llm-convert=ldc.tool.convert:sys_main",
            "llm-download=ldc.tool.download:sys_main",
            "llm-file-encoding=ldc.tool.file_encoding:sys_main",
            "llm-find=ldc.tool.find:sys_main",
            "llm-help=ldc.tool.help:sys_main",
            "llm-paste=ldc.tool.paste:sys_main",
            "llm-registry=ldc.registry:sys_main",
        ],
        "ldc.downloaders": [
            "ldc_downloaders1=ldc.downloader:ldc.downloader.Downloader"
        ],
        "ldc.readers": [
            "lcd_readers1=ldc.pretrain:ldc.api.Reader",
            "lcd_readers2=ldc.supervised.classification:ldc.api.Reader",
            "lcd_readers3=ldc.supervised.pairs:ldc.api.Reader",
            "lcd_readers4=ldc.translation:ldc.api.Reader",
        ],
        "ldc.filters": [
            "lcd_filters1=ldc.filter:ldc.api.Filter",
            "lcd_filters2=ldc.pretrain:ldc.api.Filter",
            "lcd_readers3=ldc.supervised.classification:ldc.api.Filter",
            "lcd_readers4=ldc.supervised.pairs:ldc.api.Filter",
            "lcd_filters5=ldc.translation:ldc.api.Filter",
        ],
        "ldc.writers": [
            "lcd_writers1=ldc.pretrain:seppl.io.Writer",
            "lcd_writers2=ldc.supervised.classification:seppl.io.Writer",
            "lcd_writers3=ldc.supervised.pairs:seppl.io.Writer",
            "lcd_writers4=ldc.translation:seppl.io.Writer",
        ]
    },
)

