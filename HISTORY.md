# History

Nukikata will be a couple months behind the major releases for cookiecutter at which point it will be on exact feature parity. Each update is done maintaining coverage doing it's best to not break any tests and inherit all the existing functionality of cookiecutter.

The cookiecutter history can be viewed in the [project tab](https://github.com/cookiecutter/cookiecutter/projects) and [HISTORY.md](https://github.com/cookiecutter/cookiecutter/blob/master/HISTORY.md)


## 1.7.2.3 (2020-06-23)

- Breaking change - main function returns context instead of result_directory.  This makes it much easier to use when stitching cookiecutters together as now the context can be kept namespaced per the actual context they are being called in.  This change only affects tests and those using the package as a function. The idea is that the output directory can be resolved out of scope and does not need to be returned.
- Added yaml support
- Added context_key variable. Now this defaults to the name of the context_file without the extension.  Can be overridden in cli
- Added listdir, split,
- Added coverage over non-pty requiring operators
- Convert many tests to run both from tox and local - broke `test_cookiecutter_no_input_return_project_dir`

## 1.7.2.2 (2020-06-01)

- Fixed operator call order and postgen operator logic for delayed operators
- Added proper metadata to setup.py
- Fixed compatibility with py3.6

## 1.7.2.1 (2020-06-01)

- Fixed some packaging issue

## 1.7.2.0 (2020-06-01) First release on pypi

- Added operator import logic
- Catch inputs of dict with `type` to inform operator
- Added dict and list output after jinja rendering
- Add `when` and `loop` conditionals
- Added pyinquirer operators and other basic ones like command




