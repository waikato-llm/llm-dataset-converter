import argparse
import logging
import sys
import traceback

from typing import Union, List

from ldc.core import init_logging
from ldc.core import LOGGING_LEVELS, LOGGING_INFO, set_logging_level
from huggingface_hub import hf_hub_download, snapshot_download
from huggingface_hub.constants import REPO_TYPES

HUGGINGFACE_DOWNLOAD = "llm-hf-download"

_logger = logging.getLogger(HUGGINGFACE_DOWNLOAD)


def download(repo_id: str, repo_type: str = None, filename: Union[str, List[str]] = None, revision: str = None,
             output_dir: str = None, logging_level: str = LOGGING_INFO):
    """
    Downloads the specified dataset to the output directory.

    :param repo_id: the ID of the repository/dataset to download
    :type repo_id: str
    :param repo_type: the type of the repository, see REPO_TYPES
    :type repo_type: str
    :param filename: when only to download specific file(s) rather than the whole dataset
    :type filename: str or list
    :param revision: the revision of the dataset, None for latest
    :type revision: str
    :param output_dir: the directory to store the data in, None for default Hugging Face cache dir
    :type output_dir: str
    :param logging_level: the logging level to use
    :type logging_level: str
    """
    set_logging_level(_logger, logging_level)

    if isinstance(filename, str):
        filename = [filename]

    _logger.info("Repository ID: %s" % repo_id)
    if repo_type is not None:
        _logger.info("Repository type: %s" % repo_type)
    if filename is not None:
        _logger.info("Filename(s): %s" % ", ".join(filename))
    _logger.info("Revision: %s" % ("latest" if (revision is None) else revision))
    _logger.info("Output: %s" % ("default cache dir" if (output_dir is None) else output_dir))

    if filename is None:
        path = snapshot_download(repo_id, revision=revision, local_dir=output_dir, repo_type=repo_type, local_dir_use_symlinks=False)
        _logger.info("Downloaded: %s" % path)
    else:
        for f in filename:
            path = hf_hub_download(repo_id, filename=f, revision=revision, local_dir=output_dir, repo_type=repo_type, local_dir_use_symlinks=False)
            _logger.info("Downloaded: %s" % path)


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    init_logging()
    parser = argparse.ArgumentParser(
        description="Tool for downloading files or datasets from Hugging Face (https://huggingface.co/) for local conversion.",
        prog=HUGGINGFACE_DOWNLOAD,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--repo_id", help="The name of the Hugging Face repository/dataset to download", required=True)
    parser.add_argument("-t", "--repo_type", help="The type of the repository", choices=REPO_TYPES, default=None, required=False)
    parser.add_argument("-f", "--filename", help="The name of the file to download rather than the full dataset", default=None, required=False, nargs="*")
    parser.add_argument("-r", "--revision", help="The revision of the dataset to download, omit for latest", default=None, required=False)
    parser.add_argument("-o", "--output_dir", help="The directory to store the data in, stores it in the default Hugging Face cache directory when omitted.", default=None, required=False)
    parser.add_argument("-l", "--logging_level", choices=LOGGING_LEVELS, default=LOGGING_INFO, help="The logging level to use")
    parsed = parser.parse_args(args=args)
    download(parsed.repo_id, repo_type=parsed.repo_type, filename=parsed.filename, revision=parsed.revision,
             output_dir=parsed.output_dir, logging_level=parsed.logging_level)


def sys_main() -> int:
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    """
    try:
        main()
        return 0
    except Exception:
        traceback.print_exc()
        print("Arguments: %s" % str(sys.argv[1:]), file=sys.stderr)
        return 1


if __name__ == '__main__':
    main()
