# nukikata

Japanese for `cookiecutter`: クッキーの抜き型 - Kukkī no nukikata | Direct translation: To shape or mold

[![pypi](https://img.shields.io/pypi/v/nukikata.svg)](https://pypi.python.org/pypi/nukikata)
[![python](https://img.shields.io/pypi/pyversions/nukikata.svg)](https://pypi.python.org/pypi/nukikata)
[![Build Status](https://travis-ci.org/insight-infrastructure/nukikata.svg?branch=master)](https://travis-ci.org/insight-infrastructure/nukikata)
[![codecov](https://codecov.io/gh/insight-infrastructure/nukikata/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/insight-infrastructure/nukikata?branch=master)

### Fork of

![Cookiecutter](https://raw.githubusercontent.com/cookiecutter/cookiecutter/3ac078356adf5a1a72042dfe72ebfa4a9cd5ef38/logo/cookiecutter_medium.png)

* Nukikata Documentation: [https://insight-infrastructure.github.io/nukikata](https://insight-infrastructure.github.io/nukikata)
    * [API Docs](https://insight-infrastructure.github.io/nukikata/docs/_build/html/cookiecutter.operators.html#submodules)
* Cookiecutter Documentation: [https://cookiecutter.readthedocs.io](https://cookiecutter.readthedocs.io)
* GitHub: [https://github.com/cookiecutter/cookiecutter](https://github.com/cookiecutter/cookiecutter)
* PyPI: [https://pypi.org/project/nukikata/](https://pypi.org/project/nukikata/)
* Free and open source software: [BSD license](https://github.com/nukikata/cookiecutter/blob/master/LICENSE)

[Cookiecutter](https://github.com/cookiecutter/cookiecutter) is the worlds most popular code scaffolding tool with over [4 thousand open source cookiecutters](https://github.com/search?q=cookiecutter) available today.  This fork includes many additional features including:
- Loops
- Conditionals
- Plugins

Inspired by [Ansible's](https://github.com/ansible/ansible) syntax, this project aims to be a flexible declarative CLI that is easy to write operators for to extend functionality. It was originally built to extend cookiecutter to include conditionals and loops in the configuration file format.  We are now looking at it as an upstream declarative CLI sandbox to prove out patterns that can either be integrated back into cookiecutter or fit a variety of other use cases.

## Quick Demo

```
pip3 install nukikata
nukikata https://github.com/insight-infrastructure/nukikata-demos
```

Note: If you experience installation errors try `pip3 install nukikata --no-binary :all:`.

## Features

All cookiecutter features are supported in addition to loops, conditionals, and plugins. These features are only available to supplied dictionary objects with a `type` key to trigger the associated [operator](cookiecutter/operators). Loops and conditionals are triggered by rendering [jinja](https://github.com/pallets/jinja) expressions per the example below. Other cookiecutters can be called from a single nukikata to knit together modularized components.

`nuki.yaml`
```yaml
---
name:
  type: input # Input box
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
    - flung-off-bridge: I donno
    - walk-across-bridge: What do you mean? African or European swallow?

bad_outcome:
  type: print
  statement: Wrong answer {{ nuki.name }}...
  when: "{{ nuki.outcome == 'flung-off-bridge' }}"

color_essays:
  type: input
  message: Please tell me how much you like the color {{nuki.item}}?
  default: Oh color {{nuki.item}}, you are so frickin cool... # loops over nuki.colors
  loop: "{{ nuki.colors }}"
  when: "{{ nuki.colors|length > 1 }}"

democmd:
  type: command
  command: pwd

dump_yaml:
  type: yaml
  contents: "{{ nuki }}"
  path: "{{ calling_directory }}/output.yaml"
```

Here the jinja default context key goes to the name of file - ie `{{ nuki.<> }}` but can be customized if needed. We can also see the use of a special variable

Prompts are enhanced by extending the functionality from [PyInquirer](https://github.com/CITGuru/PyInquirer) as a set of operators as noted by the types `input`, `list`, and `checkbox`. Writing new operators is super simple as seen in the `print` operator:

[`cookiecuttuer/operators/print.py`](cookiecutter/operators/print.py)
```python
class PrintOperator(BaseOperator):
    type = 'print'
    def __init__(self, *args, **kwargs):
        super(PrintOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        print(self.operator_dict['statement'])
        return self.operator_dict['statement']
```

New operator PRs welcome.  We're aiming to interface with various APIs and popular libraries to create simple ways to conditionally call and loop through popular methods.

### Operators

Over 35 different operators are currently available with more coming down the line. To understand how to use them, please refer to the [API Docs](https://insight-infrastructure.github.io/nukikata/docs/_build/html/cookiecutter.operators.html#submodules).

The main type of operators are derivations of [PyInquirer](https://github.com/CITGuru/PyInquirer) which greatly enhanced the capabilities of the original cookiecutter due to the ability to use multi-select inputs that return lists. Please inspect the [PyInquirer](https://github.com/CITGuru/PyInquirer) API docs to understand the interface. All features are supported except for `validation` and `filter` which is not supported and `when` which is implemented in jinja.

To see a number of good examples of the types of interfaces available for each operator, consider downloading the demo above and walking through the syntax.

## Note to Users and Developers

This is a very early WIP but has long term ambitions of being a sort of swiss army knife for management of configuration files and boilerplate. Please consider contributing or leaving your comments in the issues section on where you see this project going and what features you would like added.

This project intends on being an edge release of `cookiecutter` and would not have been possible were it not for the orginal maintainers of that repository.  Development in this repository is meant to be a proving ground for features that could be implemented and merged into the original `cookiecutter` repository. Please consider supporting both projects.

Windows will not have first class support. Several operators are built for POSIX systems.  PRs welcome to build in full support.  Basic features like PyInquirer style prompts are supported.
