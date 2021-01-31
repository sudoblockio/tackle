# Tackle Box

[![pypi](https://img.shields.io/pypi/v/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![python](https://img.shields.io/pypi/pyversions/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![codecov](https://codecov.io/gh/robcxyz/tackle-box/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/robcxyz/tackle-box?branch=master)

* Tackle Box Documentation: [https://robcxyz.github.io/tackle-box](https://robcxyz.github.io/tackle-box)
    * [API Docs](https://robcxyz.github.io/tackle-box/docs/_build/html/cookiecutter.operators.html#submodules) # WIP
* GitHub: [https://github.com/robcxyz/tackle-box](https://github.com/cookiecutter/cookiecutter)
* PyPI: [https://pypi.org/project/tackle-box/](https://pypi.org/project/tackle-box/)
* Free and open source software: [BSD license](https://github.com/tackle-box/cookiecutter/blob/master/LICENSE)

Tackle box is a DSL for easily creating CLIs, workflows, and generating code from templates. The framework is modular and empowered by a collection of hooks to easily extend functionality through a set of declarative plugins. Based off a fork of [cookiecutter](https://github.com/cookiecutter/cookiecutter), this tool evolved from being a code generator to connecting git repositories into a web of CLIs.

### Quick Demo

<!--  TODO: Refactor -->
```
pip3 install tackle-box
tackle https://github.com/robcxyz/tackle-demos
```

### Features

All cookiecutter features are supported in addition to loops, conditionals, and plugins. These features are only available to supplied dictionary objects with a `type` key to trigger the associated [hook](tackle/models.py). Loops and conditionals are triggered by rendering [jinja](https://github.com/pallets/jinja) expressions per the example below. Other cookiecutters can be called from a single tackle box to knit together modularized components.

`tackle.yaml`
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
  statement: Wrong answer {{ name }}... # Render the `name` variable
  when: "{{ outcome == 'flung-off-bridge' }}" # Conditionals need to evaluate as booleans

color_essays:
  type: input
  message: Please tell me how much you like the color {{item}}?
  default: Oh color {{item}}, you are so frickin cool...
  loop: "{{ colors }}" # loops over colors
  when: "{{ colors|length > 1 }}"

democmd:
  type: command # Run arbitrary system commands and return stdout
  command: pwd

output:
  type: pprint # Pretty print the output
  output: "{{ this }}" # Special var that contains a dictionary of all the values

branch:
  type: tackle
  template: https://github.com/audreyfeldroy/cookiecutter-pypackage # Call other cookiecutters
```

Each hook is called via its `type` which, in the case of the `input` hook, can be looked up in the [docs]() or by looking at the [source code]() directly.

Prompts are enhanced by extending the functionality from [PyInquirer](https://github.com/CITGuru/PyInquirer) as a set of hooks as noted by the types `input`, `select`, and `checkbox`. Writing new hooks is super simple as seen in the `print` hook:

### Hooks

[`cookiecuttuer/providers/hooks/print.py`](tackle/operators/print.py)

```python
from tackle.models import BaseHook
from typing import Union

class PrintOperator(BaseHook):
    type: str = 'print'
    out: Union[dict, list, str] = None

    def execute(self):
        print(self.out)
        return self.out
```

Hooks are built with pydantic by inheriting from the [BaseHook](tackle/models.py) that makes a number of useful methods and attributes available.

#### Base Methods

A number of useful methods are available when executing any hook. Here is a breif example of all of them being used.

```yaml
this:
  type: a_hook
  chdir: "/path/to/some/{{ item }}" # Changes to the dir before executing
  loop: # Expects a list, creates `item` and `index` variables in loop
    - foo
    - bar
    - baz
  reverse: "{{ some_boolean_variable or condition }}" # Boolean to revers the loop
  when: "{{ index >= 1 }}" # Jinja expression that evaluates to boolean to conditionally use the hook
  else: "{{ some_other_var }}" # Fallback for `when` key if false.  Can also be another hook.  
  merge: True # Merge the outputs to the upper level context
```

This hook would change the directory into the `bar` and `baz` directory for execution. For further documentation on base methods, see check out [the docs]().

#### Providers

Collections of hooks are made available through lazy loaded providers each with their own dependencies. Each provider has the following directory structure.

```bash
├── hooks
│   ├── <package>.py  # Any filename is fine
│   └── __init__.py  # Optional - Use this file to specify hook names if the provider is to be lazy loaded
├── requirements.txt
```

Providers can either force the user to install the dependencies in the `requirements.txt` when tackle is called or by inserting `hook_types = ["your_hook_name"]` into the `__init__.py` to defer initialization of the provider until it is called.  Provider requirements are then installed if they are called from a tackle script.  This was done to allow users access to a variety of hooks without them needing to install every possible dependency.  It can also be a security concern with future versions dealing with this and also exposing additional features like `commands` and `templates` to extend custom actions.

Check out the providers in `tackle/providers` to get a sense of how to build them. They are really easy to build and test.

### Hooks

Around 50 different hooks are currently available with more coming down the line. To understand how to use them, please refer to the [API Docs](https://robcxyz.github.io/tackle-box/docs/_build/html/cookiecutter.operators.html#submodules).

The main type of operators are derivations of [PyInquirer](https://github.com/CITGuru/PyInquirer) which greatly enhanced the capabilities of the original cookiecutter due to the ability to use multi-select inputs that return lists. Please inspect the [PyInquirer](https://github.com/CITGuru/PyInquirer) API docs to understand the interface. All features are supported except for `validation` and `filter` which is not supported and `when` which is implemented in jinja.

To see a number of good examples of the types of interfaces available for each operator, consider downloading the demo above and walking through the syntax.

## Note to Users and Developers

This is a very early WIP but has long term ambitions of being a sort of swiss army knife for management of configuration files and boilerplate. Please consider contributing or leaving your comments in the issues section on where you see this project going and what features you would like added.

This project intends on being an edge release of `cookiecutter` and would not have been possible were it not for the orginal maintainers of that repository.  Development in this repository is meant to be a proving ground for features that could be implemented and merged into the original `cookiecutter` repository. Please consider supporting both projects.

Windows will not have first class support. Several operators are built for POSIX systems.  PRs welcome to build in full support.  Basic features like PyInquirer style prompts are supported.
