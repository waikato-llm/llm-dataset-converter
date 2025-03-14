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
    name="llm_dataset_converter",
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
        "setuptools",
        "chardet",
        "pandas",
        "jsonlines",
        "pyarrow",
        "pyzstd",
        "huggingface-hub",
        "seppl>=0.2.13",
        "pyyaml",
        "wai.logging",
    ],
    version="0.2.6",
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
        "class_lister": [
            "ldc=ldc.class_lister",
        ],
    },
)

