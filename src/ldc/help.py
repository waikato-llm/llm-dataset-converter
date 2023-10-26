import os

from seppl import OutputProducer, InputConsumer, classes_to_str

from ldc.core import DomainHandler
from ldc.registry import available_plugins


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
