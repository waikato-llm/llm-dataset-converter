PyPi
====

Preparation:

* update all help files (`llm-help -f markdown -o plugins -l INFO`)
* update the help screen of `llm-convert` in `README.md` to have the latest list of plugins
* increment version in `setup.py`
* add new changelog section in `CHANGES.rst`
* align `DESCRIPTION.rst` with `README.md`  
* commit/push all changes

Commands for releasing on pypi.org (requires twine >= 1.8.0):

```
find -name "*~" -delete
rm dist/*
python3 setup.py clean
python3 setup.py sdist
twine upload dist/*
```


Github
======

Steps:

* start new release (version: `vX.Y.Z`)
* enter release notes, i.e., significant changes since last release
* upload `llm-dataset-converter-X.Y.Z.tar.gz` previously generated with `setup.py`
* publish


llm-dataset-converter-all
=========================

* increment minimum version to newly released one in `setup.py`
* add note to `CHANGES.rst`
