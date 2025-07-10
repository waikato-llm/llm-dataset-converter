Changelog
=========

0.2.7 (2025-07-11)
------------------

- added `set-placeholder` filter for dynamically setting (temporary) placeholders at runtime
- using `wai_logging` instead of `wai.logging` now
- added `remove-strings` filter that just removes sub-strings
- added `strip-strings` filter for stripping whitespaces from start/end of strings
- requiring `seppl>=0.2.17` now to avoid deprecated use of pkg_resources


0.2.6 (2025-03-14)
------------------

- switched to underscores in project name
- requiring seppl>=0.2.13 now
- added support for aliases
- added `discard-by-name` filter, which uses the `file` filed in the meta-data for its matching
- added placeholder support
- method `text_utils.empty_str_if_none` now handles bool/int/float as well
- CSV/TSV writers now have an `--encoding` option to use a specific encoding other than the default, e.g., UTF-8


0.2.5 (2024-12-20)
------------------

- added `setuptools` as dependency


0.2.4 (2024-07-05)
------------------

- requiring seppl>=0.2.6 now
- readers use default globs now, allowing the user to simply supply directories as input
- renamed `split` filter to `split-records` to avoid name clash with meta-data key `split` as parameter


0.2.3 (2024-05-06)
------------------

- requiring seppl>=0.2.4 now


0.2.2 (2024-05-03)
------------------

- requiring seppl>=0.2.3 now


0.2.1 (2024-05-02)
------------------

- filters `split` and `tee` now support `ClassificationData` as well
- added `metadata-from-name` filter to extract meta-data from the current input file name
- added `inspect` filter that allows inspecting data interactively as it passes through the pipeline
- added `empty_str_if_none` helper method to `ldc.text_utils` to ensure no None/null values are output with writers
- upgraded seppl to 0.2.2 and switched to using `seppl.ClassListerRegistry`


0.2.0 (2024-02-27)
------------------

- added support for XTuner conversation JSON format: `from-xtuner` and `to-xtuner`
- added filter `update-pair-data` to allow tweaking or rearranging of the data
- introduced `ldc.api` module to separate out abstract superclasses and avoid circular imports
- readers now set the 'file' meta-data value
- added `file-filter` filter for explicitly allowing/discarding records that stem from certain files (entry in meta-data: 'file')
- added `record-files` filter for recording the files that the records are based on (entry in meta-data: 'file')
- filter `pretrain-sentences-to-pairs` can now omit filling the `instruction` when using 0 as prompt step
- requiring seppl>=0.1.2 now
- added global option `-U, --unescape_unicode` to `llm-convert` tool to allow conversion of escaped unicode characters
- the `llm-append` tool now supports appending for json, jsonlines and CSV files apart from plain-text files (default)


0.1.1 (2024-02-15)
------------------

- added `classification` domain
- added `from-jsonlines-cl` reader and `to-jsonlines-cl` writer for classification data in JSON lines format
- added filter `pretrain-sentences-to-classification` to turn pretrain data into classification data (with a predefined label)
- added filter `classification-label-map` that can generate a label string/int map
- the `to-llama2-format` filter now has the `--skip_tokens` options to leave out the [INST] [/INST] tokens
- added `from-parquet-cl` reader and `to-parquet-cl` writer for classification data in Parquet database format
- added `from-csv-cl`/`from-tsv-cl` readers and `to-csv-cl`/`to-tsv-cl` writers for classification data in CSV/TSV file format


0.1.0 (2024-02-05)
------------------

- fixed output format of `to-llama2-format` filter
- `llama2-to-pairs` filter has more robust parsing now
- upgraded seppl to 0.1.0
- switched to seppl classes: Splitter, MetaDataHandler, Reader, Writer, StreamWriter, BatchWriter


0.0.5 (2024-01-24)
------------------

- added flag `-b/--force_batch` to the `llm-convert` tool which all data to be reader from the
  reader before filtering it and then passing it to the writer; useful for batch filters.
- added the `randomize-records` batch filter
- added the `--encoding ENC` option to file readers
- auto-determined encoding is now being logged (`INFO` level)
- the `LDC_ENCODING_MAX_CHECK_LENGTH` environment variable allows overriding the default
  number of bytes used for determining the file encoding in auto-detect mode
- default max number of bytes inspected for determining file encoding is now 10kb
- method `locate_files` in `base_io` no longer includes directories when expanding globs
- added tool `llm-file-encoding` for determining file encodings of text files
- added method `replace_extension` to `base_io` module for changing a files extension
  (removes any supported compression suffix first)
- stream writers (.jsonl/.txt) now work with `--force_batch` mode; the output file name
  gets automatically generated from the input file name when just using a directory for
  the output


0.0.4 (2023-12-19)
------------------

- `pairs-to-llama2` filter now has an optional `--prefix` parameter to use with the instruction
- added the `pretrain-sentences-to-pairs` filter for generating artificial prompt/response datasets from pretrain data
- requires seppl>=0.0.11 now
- the `LDC_MODULES_EXCL` environment variable is now used for specifying modules to be excluded from the registration
  process (e.g., used when generating help screens for derived libraries that shouldn't output the
  base plugins as well)
- `llm-registry` and `llm-help` now allow specifying excluded modules via `-e/--excluded_modules` option
- `to-alpaca` writer now has the `-a/--ensure_ascii` flag to enforce ASCII compatibility in the output
- added global option `-u/--update_interval` to `convert` tool to customize how often progress of # records
  processed is being output in the console (default: 1000)
- `text-length` filter now handles None values, i.e., ignores them
- locations (i.e., input/instructions/output/etc) can be specified now multiple times
- the `llm-help` tool can generate index files for all the plugins now; in case of markdown
  it will link to the other markdown files


0.0.3 (2023-11-10)
------------------

- added the `record-window` filter
- added the `llm-registry` tool for querying the registry from the command-line
- added the `replace_patterns` method to `ldc.text_utils` module
- added the `replace-patterns` filter
- added `-p/--pretty-print` flag to `to-alpaca` writer
- added `pairs-to-llama2` and `llama2-to-pairs` filter
  (since llama2 has instruction as part of the string, it is treated as pretrain data)
- added `to-llama2-format` filter for pretrain records (no [INST]...[/INST] block)
- now requiring seppl>=0.0.8 in order to raise Exceptions when encountering unknown arguments


0.0.2 (2023-10-31)
------------------

- added `text-stats` filter
- stream writers accept iterable of data records now as well to improve throughput
- `text_utils.apply_max_length` now uses simple whitespace splitting instead of
  searching for nearest word boundary to break a line, which results in a massive
  speed improvement
- fix: `text_utils.remove_patterns` no longer multiplies the generated lines when using
  more than one pattern
- added `remove-patterns` filter
- pretrain and translation text writers now buffer records by default (`-b`, `--buffer_size`)
  in order to improve throughput
- jsonlines writers for pair, pretrain and translation data are now stream writers


0.0.1 (2023-10-26)
------------------

- initial release

