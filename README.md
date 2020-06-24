# nukikata

Japanese for `cookiecutter`: クッキーの抜き型 - Kukkī no nukikata | Direct translation: To shape or mold

[![pypi](https://img.shields.io/pypi/v/nukikata.svg)](https://pypi.python.org/pypi/nukikata)
[![python](https://img.shields.io/pypi/pyversions/nukikata.svg)](https://pypi.python.org/pypi/nukikata)
[![Build Status](https://travis-ci.org/insight-infrastructure/nukikata.svg?branch=master)](https://travis-ci.org/insight-infrastructure/nukikata)
[![codecov](https://codecov.io/gh/insight-infrastructure/nukikata/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/insight-infrastructure/nukikata?branch=master)

### Fork of

![Cookiecutter](https://raw.githubusercontent.com/cookiecutter/cookiecutter/3ac078356adf5a1a72042dfe72ebfa4a9cd5ef38/logo/cookiecutter_medium.png)

[github.com/cookiecutter/cookiecutter](https://github.com/cookiecutter/cookiecutter) with additional features including:
- Loops
- Conditionals
- Plugins

Inspired by [Ansible's](https://github.com/ansible/ansible) syntax, this project aims to be a config driven CLI with a plugins based rendering and hooking capabilities.

## Quick Demo

```
pip3 install nukikata
nukikata https://github.com/insight-infrastructure/nukikata-demo-monty
curl https://raw.githubusercontent.com/insight-infrastructure/nukikata-demo-basic/master/nuki.yaml
cat output.json
```

## Features

All cookiecutter features are supported in addition to loops, conditionals, and plugins. These features are only available to supplied dictionary objects with a `type` key to trigger the associated [operator](cookiecutter/operators). Loops and conditionals are triggered by rendering [jinja](https://github.com/pallets/jinja) expressions per the example below.

`nuki.yaml`
```yaml
---
name:
  type: input
  message: What is your name?

colors:
  type: checkbox
  message: What are your favorite colors?
  choices:
    - name: blue
    - name: green
    - name: grey

wingspeed:
  type: list
  message: What is the airspeed velocity of an unladen swallow??
  choices:
    - name: I donno
    - name: What do you mean? African or European swallow?

bad_outcome:
  type: print
  statement: Wrong answer {{ nuki.name }}...
  when: "{{ 'I donno' in nuki.wingspeed }}"

color_essays:
  type: input
  message: Please tell me how much you like the color {{nuki.item}}?
  default: Oh color {{nuki.item}}, you are so frickin cool...
  loop: "{{ nuki.colors }}"
  when: "{{ nuki.colors|length > 1 }}"

democmd:
  type: command
  command: pwd

dump_json:
  type: json
  contents: "{{ nuki }}"
  path: output.json
```

Here the jinja default context key goes to the name of file - ie `{{ nuki.<> }}`

Prompts are enhanced by extending the functionality from [PyInquirer](https://github.com/CITGuru/PyInquirer) as a set of operators as noted by the types `input`, `list`, and `checkbox`. Writing new operators is super simple as seen in the `print` operator:

[`cookiecuttuer/operators/print.py`](cookiecutter/operators/print.py)
```python
class PrintOperator(BaseOperator):
    """Operator for PyInquirer type prompts."""

    type = 'print'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize PyInquirer Hook."""
        super(PrintOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )

    def execute(self):
        """Run the prompt."""
        print(self.operator_dict['statement'])
        return self.operator_dict['statement']
```

New operator PRs welcome.  We're aiming to interface with various APIs and popular libraries to create simple ways to conditionally call and loop through popular methods.

### Operators

Numerous operators are currently available with more coming down the line. Below is a current list of operators.

> Note: This is a WIP. API docs will be generated with sphinx soon to cover the operators.

The main type of operator being used are derivations of [PyInquirer](https://github.com/CITGuru/PyInquirer) which greatly enhanced the capabilities of the original cookiecutter due to the ability to use multi-select inputs that return lists. Please inspect the [PyInquirer](https://github.com/CITGuru/PyInquirer) API docs to understand the interface. All features are supported except for `validation` and `filter` which is not supported and `when` which is implemented in jinja.

Here is a short list of the operators currently supported.

**PyInquirer**

> All PyInquirer operators require `message` input

- [`checkbox`](cookiecutter/operators/checkbox.py)
    - Multi-select list
    - Inputs
        - `choices` - list of dicts with `name` as choice. See example above.
    - [PyInquirer Example](https://github.com/CITGuru/PyInquirer/blob/master/examples/checkbox.py)
    - Outputs list
- [`confirm`](cookiecutter/operators/confirm.py)
    - Verification
    - [PyInquirer Example](https://github.com/CITGuru/PyInquirer/blob/master/examples/confirm.py)
    - Outputs boolean
- [`editor`](cookiecutter/operators/editor.py)
    - Opens up editor
    - [PyInquirer Example](https://github.com/CITGuru/PyInquirer/blob/master/examples/editor.py)
    - Outputs string
- [`expand`](cookiecutter/operators/expand.py)
    - Path completion to local file
    - [PyInquirer Example](https://github.com/CITGuru/PyInquirer/blob/master/examples/expand.py)
    - Outputs string
- [`input`](cookiecutter/operators/input.py)
    - Simple input with question
    - [PyInquirer Example](https://github.com/CITGuru/PyInquirer/blob/master/examples/input.py)
    - Outputs string
- [`list`](cookiecutter/operators/list.py)
    - Single select from list
    - [PyInquirer Example](https://github.com/CITGuru/PyInquirer/blob/master/examples/list.py)
    - Outputs string
- [`rawlist`](cookiecutter/operators/rawlist.py)
    - Single select from list
    - [PyInquirer Example](https://github.com/CITGuru/PyInquirer/blob/master/examples/rawlist.py)
    - Outputs string
- [`password`](cookiecutter/operators/password.py)
    - Input that is hidden
    - [PyInquirer Example](https://github.com/CITGuru/PyInquirer/blob/master/examples/password.py)
    - Outputs string

**Python wrappers**
- [`command`](cookiecutter/operators/command.py)
    - Execute an arbitrary shell command
    - Outputs stdout as `string`
- [`jinja`](cookiecutter/operators/jinja.py)
    - Takes template as path and renders to path
    - Inputs
        - `template_path` - string
        - `output_path` - string
    - Outputs `None`
- [`json`](cookiecutter/operators/json.py)
    - Writes json to file if `contents` key supplied
    - Reads json from file
    - Requires `path` to output file
    - Outputs path to outputs or  `dict`
- [`nukikata`](cookiecutter/operators/nukikata.py)
    - Wraps calls to other nukikatas
    - Outputs project_dir
- [`print`](cookiecutter/operators/print.py)
    - Prints the statement
    - Outputs `statement` parameter
    - Useful for intermediary rendering
- [`stat`](cookiecutter/operators/stat.py)
    - Reinserts `input` parameter to the variable
    - Useful for intermediary rendering
- [`yaml`](cookiecutter/operators/yaml.py)
    - Same as `json` operator

## Note to Users and Developers

This is a very early WIP but has long term ambitions of being a sort of swiss army knife for management of configuration files and boilerplate. Please consider contributing or leaving your comments in the issues section on where you see this project going and what features you would like added. All future improvements are being migrated into github issues from a local [ttd file](TTD.md).

This project intends on being an edge release of `cookiecutter` and would not have been possible were it not for the orginal maintainers of that repository.  Development in this repository is meant to be a proving ground for features that could be implemented and merged into the original `cookiecutter` repository. Please consider supporting both projects.

Windows will not be supported and hence certain features will likely only exist in this repo compared to the original. This tool was built to handle the mountains of configuration files normally dealt with in declarative infrastructure deployments.

