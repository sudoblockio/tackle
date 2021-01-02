========
Overview
========

Input
-----

This is the directory structure for a simple tackle box / cookiecutter::

    tackle-something/
    ├── {{project_name}}/  <--------- Project template
    │   └── ...
    ├── foo.txt                      <--------- Non-templated files/dirs
    │                                            go outside
    ├── hooks                      <--------- Hooks directory
    │   └── ...
    │
    └── tackle.yaml             <--------- Prompts & default values

You must have:

* A context file - Can be `tackle.yaml`, `cookiecutter.json`, or any other file as long as specified at command line with `--context-file=my-file.yaml` input.

Optionally, you may have:

* A `{{ cookiecutter.project_name }}/` directory, where
  `project_name` is defined in your context file.

* A `hooks/` directory with either `pre_gen_project` or `post_gen_project` files in either python (`.py`) or bash (`.sh`) or arbitrary python objects derived from the `BaseHook` to be included to be called from the context file.

Beyond that, you can have whatever files/directories you want.

See https://github.com/audreyr/cookiecutter-pypackage for a real-world example
of this.

Output
------

This is what will be generated locally, in your current directory::

    mysomething/  <---------- Value corresponding to what you enter at the
    │                         project_name prompt
    │
    └── ...       <-------- Files corresponding to those in your
                            cookiecutter's `{{ cookiecutter.project_name }}/` dir
