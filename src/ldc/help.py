import argparse
import logging
import traceback

from ldc.args import HELP_FORMATS, HELP_FORMAT_TEXT, generate_plugin_usage

HELP = "llm-help"

_logger = logging.getLogger(HELP)


def output_help(plugin_name: str, help_format: str = HELP_FORMAT_TEXT, heading_level: int = 1, output: str = None):
    """
    Generates and outputs the help screen for the plugin.

    :param plugin_name: the plugin to generate the help for
    :type plugin_name: str
    :param help_format: the format to output
    :type help_format: str
    :param heading_level: the heading level to use (markdown)
    :type heading_level: int
    :param output: the file to save the output to, uses stdout if None
    :type output: str
    """
    if help_format not in HELP_FORMATS:
        raise Exception("Unknown help format: %s" % help_format)
    generate_plugin_usage(plugin_name, help_format=help_format, heading_level=heading_level, output_file=output)


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    parser = argparse.ArgumentParser(
        description="Tool for outputting help for plugins in various formats.",
        prog=HELP,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p", "--plugin_name", metavar="NAME", help="The name of the plugin to generate the help for", type=str, required=True)
    parser.add_argument("-f", "--help_format", metavar="FORMAT", help="The output format to generate", choices=HELP_FORMATS, default=HELP_FORMAT_TEXT, required=False)
    parser.add_argument("-l", "--heading_level", metavar="INT", help="The level to use for the heading", default=1, type=int, required=False)
    parser.add_argument("-o", "--output", metavar="FILE", help="The file to store the help in, outputs it to stdout if not supplied", type=str, default=None, required=False)
    parsed = parser.parse_args(args=args)
    output_help(parsed.plugin_name, help_format=parsed.help_format, heading_level=parsed.heading_level,
                output=parsed.output)


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
        print(traceback.format_exc())
        return 1


if __name__ == '__main__':
    main()
