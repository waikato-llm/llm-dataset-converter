Changelog
=========

0.0.2 (????-??-??)
------------------

- added `text-stats` filter
- stream writers accept iterable of data records now as well to improve throughput
- `text_utils.apply_max_length` now uses simple whitespace splitting instead of
  searching for nearest word boundary to break a line
- `text_utils.remove_patterns` no longer multiplies the generated lines when using
  more than one pattern
- added `remove_patterns` filter
- pretrain and translation text writers now buffer records by default (`-b`, `--buffer_size`)
  in order to improve throughput


0.0.1 (2023-10-26)
------------------

- initial release

