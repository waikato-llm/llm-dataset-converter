import os
from typing import List, Dict, Tuple, Iterable

from ldc.core import OutputProducer, InputConsumer, DomainHandler, classes_to_str
from ldc.registry import available_plugins


HELP_FORMAT_TEXT = "text"
HELP_FORMAT_MARKDOWN = "markdown"
HELP_FORMATS = [
    HELP_FORMAT_TEXT,
    HELP_FORMAT_MARKDOWN,
]


def split_args(args: List[str], handlers: List[str]) -> Dict[str, List[str]]:
    """
    Splits the command-line arguments into handler and their associated arguments.
    Special entry "" is used for global options.

    :param args: the command-line arguments to split
    :type args: list
    :param handlers: the list of valid handler names
    :type handlers: list
    :return: the dictionary for handler name / options list
    :rtype: dict
    """
    handlers = set(handlers)
    result = dict()
    last_handler = ""
    last_args = []

    for arg in args:
        if arg in handlers:
            result[last_handler] = last_args
            last_handler = arg
            last_args = []
            continue
        else:
            last_args.append(arg)

    if last_handler is not None:
        result[last_handler] = last_args

    return result


def is_help_requested(args: List[str]) -> Tuple[bool, bool, str]:
    """
    Checks whether help was requested.

    :param args: the arguments to check
    :type args: list
    :return: the tuple of help requested: (help_requested, plugin_details, plugin_name)
    :rtype: tuple
    """
    help_requested = False
    plugin_details = False
    plugin_name = None
    for index, arg in enumerate(args):
        if (arg == "-h") or (arg == "--help"):
            help_requested = True
            break
        if arg == "--help-all":
            help_requested = True
            plugin_details = True
            break
        if arg == "--help-plugin":
            help_requested = True
            if index < len(args) - 1:
                plugin_name = args[index + 1]
            break
    return help_requested, plugin_details, plugin_name


def enumerate_plugins(plugins: Iterable[str], prefix: str = "", width: int = 72) -> str:
    """
    Turns the list of plugin names into a string.

    :param plugins: the plugin names to turn into a string
    :type plugins: Iterable
    :param prefix: the prefix string to use for each line
    :type prefix: str
    :param width: the maximum width of the string before adding a newline
    :type width: int
    :return: the generated string
    :rtype: str
    """
    result = []
    line = prefix
    for plugin in sorted(plugins):
        if (len(line) > 0) and (line[-1] != " "):
            line += ", "
        if len(line) + len(plugin) >= width:
            result.append(line)
            line = prefix + plugin
        else:
            line += plugin
    if len(line) > 0:
        result.append(line)
    return "\n".join(result)


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
