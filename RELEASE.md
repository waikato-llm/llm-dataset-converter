PyPi
====

Preparation:

* update all help files (`llm-help -f markdown -o plugins -l INFO`)
* update the `entry_points` section in `setup.py` (`llm-entry-points`)
* increment version in `setup.py`
* add new changelog section in `CHANGES.rst`
* align `DESCRIPTION.rst` with `README.md`  
* commit/push all changes

Commands for releasing on pypi.org (requires twine >= 1.8.0):

```
find -name "*~" -delete
rm dist/*
./venv/bin/python setup.py clean
./venv/bin/python setup.py sdist
./venv/bin/twine upload dist/*
```


Github
======

Steps:

* start new release (version: `vX.Y.Z`)
* enter release notes, i.e., significant changes since last release
* upload `llm-dataset-converter-X.Y.Z.tar.gz` previously generated with `setyp.py`
* publish


