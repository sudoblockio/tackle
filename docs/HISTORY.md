# History

Tackle Box was originally intended to stay in line with cookiecutter until there were simply too many differences for the changes to be reconciled. Any changes to cookiecutter will be brought over to maintain compatibility though the two tools are now split.

The cookiecutter history can be viewed in the [project tab](https://github.com/cookiecutter/cookiecutter/projects) and [HISTORY.md](https://github.com/cookiecutter/cookiecutter/blob/master/HISTORY.md)

## Tackle Box History

### v0.1.0 (2020-12-X)
- Added providers and moved all operators into hooks


## Cookiecutter History

Prior to permanently splitting into Tackle Box.

### 2.0.0.3 (2020-8-5)
- Added tracking of whether reading `cookiecutter.*` context files which then informs whether the rendered values are interpretted literally or as strings.  Maintains support for old style rendering where users relied on having the lists, dicts, and booleans render as strings vs literals.

### 2.0.0.2 (2020-8-4)
- Modified yaml operator adding several methods
- Refactor list to select operator
- Added web, copy, move, dicts, lists operators

### 2.0.0.1 (2020-07-28)
- Added special variable `calling_directory` to preserve path regardless of context changing in remote nukikata calls.
- Fixing listdir and list operators

### 2.0.0.0 (2020-07-27)
- Added no_input to operator level discovery
- Added basic AWS, GCP, Azure, and DigitalOcean operators
- Extended yaml operator to have regex remove, update, and merging functionalities both in place and on write.
- Default `template` input to main to `.`.
- Added `index` to loop to output count in loop.
- Added `index` parameter to `list` and `checkbox` pyinquirer operators.
- Merged changes as of this date from cookiecutter 2.0.0
- Added numerous new operators
- Added warning for unknown operator type
- Added `chdir` to operator allowing temporary working directory context to be shifted
- Added `block` operator which uncovered defficiencies in how we are currently handling the running of the context in the operators

### 1.7.2.3 (2020-06-23)

- Breaking change - main function returns context instead of result_directory.  This makes it much easier to use when stitching cookiecutters together as now the context can be kept namespaced per the actual context they are being called in.  This change only affects tests and those using the package as a function. The idea is that the output directory can be resolved out of scope and does not need to be returned.
- Added yaml support
- Added context_key variable. Now this defaults to the name of the context_file without the extension.  Can be overridden in cli
- Added listdir, split,
- Added coverage over non-pty requiring operators
- Convert many tests to run both from tox and local - broke `test_cookiecutter_no_input_return_project_dir`

### 1.7.2.2 (2020-06-15)

- Fixed operator call order and postgen operator logic for delayed operators
- Added proper metadata to setup.py
- Fixed compatibility with py3.6

### 1.7.2.1 (2020-06-01)

- Fixed some packaging issue

### 1.7.2.0 (2020-06-01) First release on pypi

- Added operator import logic
- Catch inputs of dict with `type` to inform operator
- Added dict and list output after jinja rendering
- Add `when` and `loop` conditionals
- Added pyinquirer operators and other basic ones like command




