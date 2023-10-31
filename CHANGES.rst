Changelog
=========

0.0.3 (????-??-??)
------------------

- added the `record-window` filter
- ...


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

