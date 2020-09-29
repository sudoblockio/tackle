# Tackle Box

[![pypi](https://img.shields.io/pypi/v/nukikata.svg)](https://pypi.python.org/pypi/nukikata)
[![python](https://img.shields.io/pypi/pyversions/nukikata.svg)](https://pypi.python.org/pypi/nukikata)
[![Build Status](https://travis-ci.org/insight-infrastructure/nukikata.svg?branch=master)](https://travis-ci.org/insight-infrastructure/nukikata)
[![codecov](https://codecov.io/gh/insight-infrastructure/nukikata/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/insight-infrastructure/nukikata?branch=master)

* Tackle Box Documentation: [https://insight-infrastructure.github.io/nukikata](https://insight-infrastructure.github.io/nukikata)
    * [API Docs](https://insight-infrastructure.github.io/nukikata/docs/_build/html/cookiecutter.operators.html#submodules)
* Cookiecutter Documentation: [https://cookiecutter.readthedocs.io](https://cookiecutter.readthedocs.io)
* GitHub: [https://github.com/cookiecutter/cookiecutter](https://github.com/cookiecutter/cookiecutter)
* PyPI: [https://pypi.org/project/nukikata/](https://pypi.org/project/nukikata/)
* Free and open source software: [BSD license](https://github.com/nukikata/cookiecutter/blob/master/LICENSE)

Tackle box is a DSL for easily creating CLIs, workflows, and generating code from templates. The framework is modular and empowered by a collection of hooks to easily extend functionality. Based off a fork of [cookiecutter](https://github.com/cookiecutter/cookiecutter), this tool evolved from being a code generator to connecting git repositories into a web of CLIs.

> Note: Tackle box is undergoing several refactors.  Expect many changes.

## Quick Demo

<!--  TODO: Refactor -->
```
pip3 install nukikata
nukikata https://github.com/insight-infrastructure/nukikata-demos
```

Note: If you experience installation errors try `pip3 install nukikata --no-binary :all:`.

## Features

All cookiecutter features are supported in addition to loops, conditionals, and plugins. These features are only available to supplied dictionary objects with a `type` key to trigger the associated [hook](cookiecutter/operators). Loops and conditionals are triggered by rendering [jinja](https://github.com/pallets/jinja) expressions per the example below. Other cookiecutters can be called from a single nukikata to knit together modularized components.

`nuki.yaml`
```yaml
---
name:
  type: input # Input prompt which is stored in `name`
  message: What is your name?

colors:
  type: checkbox # Multi selector - returns a list
  message: What are your favorite colors?
  choices:
    - blue
    - green
    - grey

outcome:
  type: select # Single selector - returns a string
  message: What is the airspeed velocity of an unladen swallow??
  choices:
    - flung-off-bridge: I donno # Map for choices interpretted as {key: question}
    - walk-across-bridge: What do you mean? African or European swallow?

bad_outcome:
  type: print
  statement: Wrong answer {{ nuki.name }}... # Render the `name` variable
  when: "{{ nuki.outcome == 'flung-off-bridge' }}" # Conditionals are rendered json

color_essays:
  type: input
  message: Please tell me how much you like the color {{nuki.item}}?
  default: Oh color {{nuki.item}}, you are so frickin cool...
  loop: "{{ nuki.colors }}" # loops over nuki.colors
  when: "{{ nuki.colors|length > 1 }}"

democmd:
  type: command # Run arbitrary system commands and return stdout
  command: pwd

dump_yaml:
  type: yaml # Read / write yaml
  contents: "{{ nuki }}"
  path: "{{ calling_directory }}/output.yaml"
```

Here the jinja default context key goes to the name of file - ie `{{ nuki.<> }}` but can be customized if needed. We can also see the use of a special variable

Prompts are enhanced by extending the functionality from [PyInquirer](https://github.com/CITGuru/PyInquirer) as a set of hooks as noted by the types `input`, `list`, and `checkbox`. Writing new hooks is super simple as seen in the `print` hook:

[`cookiecuttuer/operators/print.py`](cookiecutter/operators/print.py)

```python
class PrintOperator(BaseOperator):
    type: str = 'print'
    out: Union[Dict, List, str] = None

    def execute(self):
        print(self.out)
        return self.out
```

Hooks are built with pydantic by inheriting from the [BaseOperator]() that makes a number of useful methods and attributes available. New hook PRs welcome. Currently working on a provider based system to allow for dynamic importing of dependencies.

### Hooks

Around 50 different hooks are currently available with more coming down the line. To understand how to use them, please refer to the [API Docs](https://insight-infrastructure.github.io/nukikata/docs/_build/html/cookiecutter.operators.html#submodules).

The main type of operators are derivations of [PyInquirer](https://github.com/CITGuru/PyInquirer) which greatly enhanced the capabilities of the original cookiecutter due to the ability to use multi-select inputs that return lists. Please inspect the [PyInquirer](https://github.com/CITGuru/PyInquirer) API docs to understand the interface. All features are supported except for `validation` and `filter` which is not supported and `when` which is implemented in jinja.

To see a number of good examples of the types of interfaces available for each operator, consider downloading the demo above and walking through the syntax.

## Note to Users and Developers

This is a very early WIP but has long term ambitions of being a sort of swiss army knife for management of configuration files and boilerplate. Please consider contributing or leaving your comments in the issues section on where you see this project going and what features you would like added.

This project intends on being an edge release of `cookiecutter` and would not have been possible were it not for the orginal maintainers of that repository.  Development in this repository is meant to be a proving ground for features that could be implemented and merged into the original `cookiecutter` repository. Please consider supporting both projects.

Windows will not have first class support. Several operators are built for POSIX systems.  PRs welcome to build in full support.  Basic features like PyInquirer style prompts are supported.
