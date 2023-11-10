Changelog
=========

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

