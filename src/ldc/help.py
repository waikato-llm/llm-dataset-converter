import argparse
import logging
import os
import sys
import traceback

from typing import List

from ldc.registry import register_plugins, available_plugins
from ldc.core import init_logging, set_logging_level, LOGGING_WARN, LOGGING_LEVELS
from ldc.core import DomainHandler
from seppl import OutputProducer, InputConsumer, classes_to_str

HELP = "llm-help"

_logger = logging.getLogger(HELP)


HELP_FORMAT_TEXT = "text"
HELP_FORMAT_MARKDOWN = "markdown"
HELP_FORMATS = [
    HELP_FORMAT_TEXT,
    HELP_FORMAT_MARKDOWN,
]


def generate_plugin_usage(plugin_name: str, help_format: str = HELP_FORMAT_TEXT, heading_level: int = 1,
                          output_path: str = None):
    """
    Generates the usage help screen for the specified plugin.

    :param plugin_name: the plugin to generate the usage for (name used on command-line)
    :type plugin_name: str
    :param help_format: the format to use for the output
    :type help_format: str
    :param heading_level: the level to use for the heading (markdown)
    :type heading_level: int
    :param output_path: the directory (automatically generates output name from plugin name and output format) or file to store the generated help in, uses stdout if None
    :type output_path: str
    """
    if help_format not in HELP_FORMATS:
        raise Exception("Unhandled help format: %s" % help_format)

    plugin = available_plugins()[plugin_name]

    result = ""
    if help_format == HELP_FORMAT_TEXT:
        suffix = ".txt"
        result += "\n" + plugin_name + "\n" + "=" * len(plugin_name) + "\n"
        if isinstance(plugin, DomainHandler):
            result += "domain(s): " + ", ".join(plugin.domains()) + "\n"
        if isinstance(plugin, InputConsumer):
            result += "accepts: " + classes_to_str(plugin.accepts()) + "\n"
        if isinstance(plugin, OutputProducer):
            result += "generates: " + classes_to_str(plugin.generates()) + "\n"
        result = result.strip()
        result += "\n\n"
        result += plugin.format_help() + "\n"
    elif help_format == HELP_FORMAT_MARKDOWN:
        suffix = ".md"
        result += "#"*heading_level + " " + plugin_name + "\n"
        result += "\n"
        if isinstance(plugin, DomainHandler):
            result += "* domain(s): " + ", ".join(plugin.domains()) + "\n"
        if isinstance(plugin, InputConsumer):
            result += "* accepts: " + classes_to_str(plugin.accepts()) + "\n"
        if isinstance(plugin, OutputProducer):
            result += "* generates: " + classes_to_str(plugin.generates()) + "\n"
        result = result.strip()
        result += "\n\n"
        result += plugin.description() + "\n"
        result += "\n"
        result += "```\n"
        result += plugin.format_help()
        result += "```\n"
    else:
        raise Exception("Unhandled help format: %s" % help_format)

    if output_path is None:
        print(result)
    else:
        if os.path.isdir(output_path):
            output_file = os.path.join(output_path, plugin.name() + suffix)
        else:
            output_file = output_path
        with open(output_file, "w") as fp:
            fp.write(result)


def output_help(modules: List[str] = None, plugin_name: str = None, help_format: str = HELP_FORMAT_TEXT, heading_level: int = 1, output: str = None):
    """
    Generates and outputs the help screen for the plugin.

    :param modules: the modules to generate the entry points for
    :type modules: list
    :param plugin_name: the plugin to generate the help for, None if for all
    :type plugin_name: str
    :param help_format: the format to output
    :type help_format: str
    :param heading_level: the heading level to use (markdown)
    :type heading_level: int
    :param output: the dir/file to save the output to, uses stdout if None
    :type output: str
    """
    register_plugins(modules)
    if help_format not in HELP_FORMATS:
        raise Exception("Unknown help format: %s" % help_format)
    if (plugin_name is None) and ((output is None) or (not os.path.isdir(output))):
        raise Exception("When generating the help for all plugins, the output must be a directory: %s" % output)
    if plugin_name is None:
        plugin_names = available_plugins().keys()
    else:
        plugin_names = [plugin_name]
    for p in plugin_names:
        _logger.info("Generating help (%s): %s" % (help_format, p))
        generate_plugin_usage(p, help_format=help_format, heading_level=heading_level, output_path=output)


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    init_logging()
    parser = argparse.ArgumentParser(
        description="Tool for outputting help for plugins in various formats.",
        prog=HELP,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--modules", metavar="PACKAGE", help="The names of the module packages, uses the default ones if not provided.", default=None, type=str, required=False, nargs="*")
    parser.add_argument("-p", "--plugin_name", metavar="NAME", help="The name of the plugin to generate the help for, generates it for all if not specified", default=None, type=str, required=False)
    parser.add_argument("-f", "--help_format", metavar="FORMAT", help="The output format to generate", choices=HELP_FORMATS, default=HELP_FORMAT_TEXT, required=False)
    parser.add_argument("-L", "--heading_level", metavar="INT", help="The level to use for the heading", default=1, type=int, required=False)
    parser.add_argument("-o", "--output", metavar="PATH", help="The directory or file to store the help in; outputs it to stdout if not supplied; if pointing to a directory, automatically generates file name from plugin name and help format", type=str, default=None, required=False)
    parser.add_argument("-l", "--logging_level", choices=LOGGING_LEVELS, default=LOGGING_WARN, help="The logging level to use")
    parsed = parser.parse_args(args=args)
    set_logging_level(_logger, parsed.logging_level)
    output_help(modules=parsed.modules, plugin_name=parsed.plugin_name, help_format=parsed.help_format,
                heading_level=parsed.heading_level, output=parsed.output)


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
        print("options: %s" % str(sys.argv[1:]), file=sys.stderr)
        return 1


if __name__ == '__main__':
    main()
