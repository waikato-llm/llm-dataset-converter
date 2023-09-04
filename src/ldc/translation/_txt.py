import argparse
import os
import re
from typing import Iterable, List, Union

from ldc.core import LOGGING_WARN, domain_suffix
from ldc.io import locate_files, open_file, generate_output, is_compressed
from ._core import TranslationData, TranslationReader, StreamTranslationWriter


PH_TAB = "{TAB}"
""" placeholder for tab. """

PH_LANG = "{LANG}"
""" placeholder for the language. """

PH_ID = "{ID}"
""" placeholder for the ID. """

PH_CONTENT = "{CONTENT}"
""" placeholder for the content/text. """


class TxtTranslationReader(TranslationReader):
    """
    Reader for plain text files.
    """

    def __init__(self, source: Union[str, List[str]] = None,
                 col_id: str = None, col_lang: str = None, col_content: str = None, col_sep: str = ":",
                 lang_in_id: bool = False, expr_lang: str = None, expr_id: str = None,
                 logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param logging_level: the logging level to use
        :param col_id: the 1-based index of the column containing the ID
        :type col_id: str
        :param col_lang: the 1-based index of the column containing the language, can be None
        :type col_lang: str
        :param col_content: the 1-based index of the column containing the content
        :type col_content: str
        :param col_sep: the column separator
        :type col_sep: str
        :param lang_in_id: whether the language is part of the ID column
        :type lang_in_id: bool
        :param expr_lang: the regexp to extract the language as first group (only if lang_in_id=True)
        :type expr_lang: str
        :param expr_id: the regexp to extract the actual ID as first group  (only if lang_in_id=True)
        :type expr_id: str
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.source = source
        self.col_id = col_id
        self.idx_id = -1
        self.col_lang = col_lang
        self.idx_lang = -1
        self.col_content = col_content
        self.idx_content = -1
        self.col_sep = col_sep
        self.lang_in_id = lang_in_id
        self.expr_lang = expr_lang
        self.pattern_lang = None
        self.expr_id = expr_id
        self.pattern_id = None
        self._inputs = None
        self._current_input = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-txt-" + domain_suffix(self)

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Reads translation data from plain text files, with each line representing a record for one specific language."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the text file(s) to read; glob syntax is supported", required=True, nargs="+")
        parser.add_argument("--col_id", metavar="COL", type=str, default=None, help="The 1-based index of the column with the row IDs (gets stored under 'id' in meta-data)", required=False)
        parser.add_argument("--col_lang", metavar="COL", type=str, default=None, help="The 1-based of the column with the language ID", required=False)
        parser.add_argument("--col_content", metavar="COL", type=str, default=None, help="The 1-based of the column with the text content", required=True)
        parser.add_argument("--col_sep", type=str, default=":", help="Separator between data columns, use " + PH_TAB + ".")
        parser.add_argument("--lang_in_id", action="store_true", help="Whether the language is part in the ID column.", required=False)
        parser.add_argument("--expr_lang", type=str, default="([a-z][a-z]).*", help="The regular expression for parsing the ID column and extracting the language as first group of the expression (only if --lang_in_id).")
        parser.add_argument("--expr_id", type=str, default="[a-z][a-z]-(.*)", help="The regular expression for parsing the ID column and extracting the actual ID as first group of the expression (only if --lang_in_id).")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.source = ns.input
        self.col_id = ns.col_id
        self.col_lang = ns.col_lang
        self.col_content = ns.col_content
        self.col_sep = ns.col_sep
        self.lang_in_id = ns.lang_in_id
        self.expr_lang = ns.expr_lang
        self.expr_id = ns.expr_id

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, fail_if_empty=True)

        try:
            self.idx_id = int(self.col_id) - 1
        except:
            self.idx_id = -1
        try:
            self.idx_lang = int(self.col_lang) - 1
        except:
            self.idx_lang = -1
        try:
            self.idx_content = int(self.col_content) - 1
        except:
            self.idx_content = -1

        if self.idx_id == -1:
            raise Exception("No column specified for the ID!")
        if self.idx_content == -1:
            raise Exception("No column specified for the content!")

        self.pattern_id = None
        self.pattern_lang = None
        if self.lang_in_id:
            self.pattern_id = re.compile(self.expr_id)
            self.pattern_lang = re.compile(self.expr_lang)
        elif self.col_lang == -1:
            raise Exception("Language must either be in a separate column or part of the ID column!")

    def read(self) -> Iterable[TranslationData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: TranslationData
        """
        self.finalize()

        for input_file in self._inputs:
            self.session.current_input = input_file
            self.logger().info("Reading from: " + str(input_file))

            curr_id = None
            translations = None
            if self.col_sep == PH_TAB:
                sep = "\t"
            else:
                sep = self.col_sep

            with open_file(self.session.current_input, mode="r") as fp:
                lines = fp.readlines()
            self.session.input_changed = True
            for line in lines:
                old_id = curr_id
                cells = line.strip().split(sep)
                cells = [x.strip() for x in cells]
                if self.lang_in_id:
                    m_id = self.pattern_id.match(cells[self.idx_id])
                    if m_id is None:
                        self.logger().warning("Failed to extract ID from: %s" % cells[self.idx_id])
                        continue
                    curr_id = m_id.group(1)
                    m_lang = self.pattern_lang.match(cells[self.idx_id])
                    if m_lang is None:
                        self.logger().warning("Failed to extract language from: %s" % cells[self.idx_id])
                        continue
                    lang = m_lang.group(1)
                else:
                    curr_id = cells[self.idx_id]
                    lang = cells[self.idx_lang]

                # group finished?
                if curr_id != old_id:
                    if translations is not None:
                        meta = {"id": old_id}
                        yield TranslationData(translations=translations, meta=meta)
                    translations = dict()

                translations[lang] = cells[self.idx_content]

            if len(translations) > 0:
                meta = {"id": curr_id}
                yield TranslationData(translations=translations, meta=meta)

        self._inputs = []

    def has_finished(self) -> bool:
        """
        Returns whether reading has finished.

        :return: True if finished
        :rtype: bool
        """
        return len(self._inputs) == 0


class TxtTranslationWriter(StreamTranslationWriter):
    """
    Writer for the plain text files.
    """

    def __init__(self, target: str = None, num_digits: int = 6, line_format: str = "%s-%s: %s" % (PH_LANG, PH_ID, PH_CONTENT),
                 logging_level: str = LOGGING_WARN):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param num_digits: the number of digits to use for the output file names
        :type num_digits: int
        :param line_format: the format for the line, available placeholders: {LANG}, {ID}, {CONTENT}
        :type line_format: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.target = target
        self.num_digits = num_digits
        self.line_format = line_format
        self._output = None
        self._writer = None
        self._concatenate = False
        self._first_item = True
        self._fname_format = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "to-txt-" + domain_suffix(self)

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Writes translation data to plain text files.\n" \
               + "When providing an output directory, either uses the current session counter as the filename or, " \
               + "if present, the 'id' value from the meta-data.\n" \
               + "When providing an output file, all incoming content will be concatenated in this one file. " \
               + "Compression is not available in this case due to the streaming context."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path to the directory or file to write to", required=True)
        parser.add_argument("-d", "--num_digits", metavar="NUM", type=int, default=6, help="The number of digits to use for the filenames", required=False)
        parser.add_argument("-f", "--line_format", metavar="FORMAT", type=str, default="%s-%s: %s" % (PH_LANG, PH_ID, PH_CONTENT), help="The format for the lines in the text file", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.target = ns.output
        self.num_digits = ns.num_digits
        self.line_format = ns.line_format

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._first_item = True
        self._fname_format = "%0" + str(self.num_digits) + "d.txt"
        if os.path.exists(self.target) and os.path.isdir(self.target):
            self._concatenate = False
        else:
            self._concatenate = True
            if is_compressed(self.target):
                raise Exception("Cannot use compression when concatenating due to streaming!")

    def _write_data(self, fp, id, data: TranslationData):
        """
        Writes the translation data to the file-like object.

        :param fp: the file-like object to use
        :param id: the ID of the translation
        :param data: the translation data to write
        :type data: TranslationData
        """
        for lang in data.translations.keys():
            line = self.line_format
            line = line.replace(PH_LANG, lang)
            line = line.replace(PH_ID, str(id))
            line = line.replace(PH_CONTENT, data.translations[lang])
            fp.write(line)
            fp.write("\n")

    def write_stream(self, data: TranslationData):
        """
        Saves the data one by one.

        :param data: the data to write
        :type data: TranslationData
        """
        if "id" in data.meta:
            id_ = data.meta["id"]
        else:
            id_ = self.session.count

        if self._concatenate:
            mode = "w" if self._first_item else "a"
            self._first_item = False
            with open(self.target, mode) as fp:
                self._write_data(fp, id_, data)
        else:
            try:
                fname = self._fname_format % int(id_)
            except:
                fname = str(id_) + ".txt"
            output = generate_output(fname, self.target, ".txt", self.session.options.compression)
            with open(output, "w") as fp:
                self._write_data(fp, id_, data)
