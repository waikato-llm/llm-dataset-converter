import argparse
import logging
import os
import sys
import traceback
from typing import List, Optional

from wai.logging import init_logging, set_logging_level, add_logging_level
from ldc.core import ENV_LLM_LOGLEVEL
from ldc.help import generate_plugin_usage, HELP_FORMATS, HELP_FORMAT_TEXT, HELP_FORMAT_MARKDOWN
from ldc.registry import register_plugins, available_plugins
from ldc.registry import available_downloaders, available_readers, available_filters, available_writers

HELP = "llm-help"

_logger = logging.getLogger(HELP)


def _add_plugins_to_index(heading: str, plugins: dict, help_format: str, lines: list):
    """
    Appends a plugin section to the output list.

    :param heading: the heading of the section
    :type heading: str
    :param plugins: the plugins dictionary to add
    :type plugins: dict
    :param help_format: the type of output to generate
    :type help_format: str
    :param lines: the output lines to append the output to
    :type lines: list
    """
    plugin_names = sorted(plugins.keys())
    if len(plugin_names) == 0:
        return
    if help_format == HELP_FORMAT_MARKDOWN:
        lines.append("## " + heading)
        for name in plugin_names:
            lines.append("* [%s](%s.md)" % (name, name))
        lines.append("")
    elif help_format == HELP_FORMAT_TEXT:
        lines.append(heading)
        lines.append("-" * len(heading))
        for name in plugin_names:
            lines.append("- %s" % name)
        lines.append("")
    else:
        raise Exception("Unsupported format for index: %s" % help_format)


def output_help(modules: List[str] = None, excluded_modules: Optional[List[str]] = None, plugin_name: str = None,
                help_format: str = HELP_FORMAT_TEXT, heading_level: int = 1, output: str = None, index: str = None):
    """
    Generates and outputs the help screen for the plugin.

    :param modules: the modules to generate the entry points for
    :type modules: list
    :param excluded_modules: the list of modules to exclude
    :type excluded_modules: list
    :param plugin_name: the plugin to generate the help for, None if for all
    :type plugin_name: str
    :param help_format: the format to output
    :type help_format: str
    :param heading_level: the heading level to use (markdown)
    :type heading_level: int
    :param output: the dir/file to save the output to, uses stdout if None
    :type output: str
    :param index: the index file to generate in the output directory, ignored if None
    :type index: str
    """
    register_plugins(modules=modules, excluded_modules=excluded_modules)
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

    if index is not None:
        header_lines = []
        if help_format == HELP_FORMAT_MARKDOWN:
            header_lines.append("# llm-dataset-converter plugins")
            header_lines.append("")
        elif help_format == HELP_FORMAT_TEXT:
            heading = "llm-dataset-converter plugins"
            header_lines.append(heading)
            header_lines.append("=" * len(heading))
            header_lines.append("")
        else:
            raise Exception("Unsupported format for index: %s" % help_format)
        plugin_lines = []
        _add_plugins_to_index("Downloaders", available_downloaders(), help_format, plugin_lines)
        _add_plugins_to_index("Readers", available_readers(), help_format, plugin_lines)
        _add_plugins_to_index("Filters", available_filters(), help_format, plugin_lines)
        _add_plugins_to_index("Writers", available_writers(), help_format, plugin_lines)
        if len(plugin_lines) < 0:
            print("No plugins listed, skipping output of index file.")
        else:
            index_file = os.path.join(output, index)
            os.makedirs(os.path.dirname(index_file), exist_ok=True)
            with open(index_file, "w") as fp:
                fp.write("\n".join(header_lines))
                fp.write("\n".join(plugin_lines))


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    init_logging(env_var=ENV_LLM_LOGLEVEL)
    parser = argparse.ArgumentParser(
        description="Tool for outputting help for plugins in various formats.",
        prog=HELP,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--modules", metavar="PACKAGE", help="The names of the module packages, uses the default ones if not provided.", default=None, type=str, required=False, nargs="*")
    parser.add_argument("-e", "--excluded_modules", type=str, default=None, help="The comma-separated list of modules to excluded.", required=False)
    parser.add_argument("-p", "--plugin_name", metavar="NAME", help="The name of the plugin to generate the help for, generates it for all if not specified", default=None, type=str, required=False)
    parser.add_argument("-f", "--help_format", metavar="FORMAT", help="The output format to generate", choices=HELP_FORMATS, default=HELP_FORMAT_TEXT, required=False)
    parser.add_argument("-L", "--heading_level", metavar="INT", help="The level to use for the heading", default=1, type=int, required=False)
    parser.add_argument("-o", "--output", metavar="PATH", help="The directory or file to store the help in; outputs it to stdout if not supplied; if pointing to a directory, automatically generates file name from plugin name and help format", type=str, default=None, required=False)
    parser.add_argument("-i", "--index", metavar="FILE", help="The file in the output directory to generate with an overview of all plugins, grouped by type (in markdown format, links them to the other generated files)", type=str, default=None, required=False)
    add_logging_level(parser)
    parsed = parser.parse_args(args=args)
    set_logging_level(_logger, parsed.logging_level)
    output_help(modules=parsed.modules, excluded_modules=parsed.excluded_modules,
                plugin_name=parsed.plugin_name, help_format=parsed.help_format,
                heading_level=parsed.heading_level, output=parsed.output,
                index=parsed.index)


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
