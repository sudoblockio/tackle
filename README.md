# Tackle Box

[![pypi](https://img.shields.io/pypi/v/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![python](https://img.shields.io/pypi/pyversions/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![codecov](https://codecov.io/gh/robcxyz/tackle-box/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/robcxyz/tackle-box?branch=master)

* Tackle Box Documentation: [https://robcxyz.github.io/tackle-box](https://robcxyz.github.io/tackle-box)
    * [API Docs](https://robcxyz.github.io/tackle-box/docs/_build/html/cookiecutter.operators.html#submodules) # WIP
* GitHub: [https://github.com/robcxyz/tackle-box](https://github.com/cookiecutter/cookiecutter)
* PyPI: [https://pypi.org/project/tackle-box/](https://pypi.org/project/tackle-box/)
* Free and open source software: [BSD license](https://github.com/tackle-box/cookiecutter/blob/master/LICENSE)

Tackle box is a structured data parser that employs a collection of hooks to turn any yaml / json file into a CLI. Created originally as a fork of cookiecutter, this project evolved from being a code generator to a full-blown configuration language reeling in a wide variety of use cases.  The syntax is easy to learn and runs out of the box with over 100 hooks which can easily be extended by importing additional providers or simply writing your own hook in less than a minute.

### Demos

Tackle box has a wide variety of use cases spanning from building code templates from specs (OpenAPI )

```
pip3 install tackle-box
tackle https://github.com/robcxyz/tackle-demos
```

### Syntax

Parse any yaml / json file by running `tackle <file name>`.  Syntax can call hooks in either compact form with arguments or in expanded form with key value arguments. For instance to prompt a user to fill in variables, we could use hooks from the PyInquirer provider such as [input](), [checkbox](), and [select]().

```yaml
---
# Compact form
name<-: input What is your name?  # Input prompt which is stored in `name`
# Here `input` is a hook that takes a message as its argument.
# Hooks are triggered whenever we see `<-`

# Mixed compact and expanded form
favorite: # Arbitrary nesting of keys and lists supported
  colors:
    <-: checkbox What are your favorite colors?  # Multi selector - returns a list
    choices:
      - blue
      - green
      - grey

# Expanded form
outcome:
  <-: select # Single selector - returns a string
  message: What is the airspeed velocity of an unladen swallow??
  choices:
    - flung-off-bridge: I donno # Map for choices interpretted as {key: question}
    - walk-across-bridge: What do you mean? African or European swallow?
```

Every single line is rendered as a Jinja template allowing conditionals and loops. For instance,

```yaml
bad_outcome:
  <: print Wrong answer {{ name }}... # Render the `name` variable
  if: outcome == 'flung-off-bridge' # Strings are rendered  by default - no need to wrap with braces

color_essays:
  <: input Please tell me how much you like the color {{item}}?
  default: Oh color {{item}}, you are so frickin cool...
  for: favorite.colors # loops over colors from prior question - strings rendered by default.
  if: favorite.colors | length > 1
  else: Who doesn't like colors?
```


```yaml
demo:
  cmd<-: command curl https://postman-echo.com/get # Run arbitrary system commands and return stdout****
  requests<-: get https://postman-echo.com/get # Or use the get hook.  Both are equivalent. 

branching:
  files: path/to/a/yaml/or/json/file.yml 
  repos<-: github.com/robcxyz/tackle-demo # Call other tackle boxes 
```

Each hook is called via its `type` which, in the case of the `input` hook, can be looked up in the [docs]() or by looking at the [source code]() directly.

Prompts are enhanced by extending the functionality from [PyInquirer](https://github.com/CITGuru/PyInquirer) as a set of hooks as noted by the types `input`, `select`, and `checkbox`. Writing new hooks is super simple as seen in the `print` hook:

### Hooks

[`tackle/providers/system/hooks/print.py`](tackle/providers/system/hooks/print.py)
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

A number of useful methods are available when executing any hook. Here is a brief example of all of them being used.

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
  merge: True # Merge the outputs to the upper level context.  Only for dict outputs.
```

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

This project intends on being an edge release of `cookiecutter` and .  Development in this repository is meant to be a proving ground for features that could be implemented and merged into the original `cookiecutter` repository. Please consider supporting both projects.

This project would not have been possible were it not for the orginal authors of cookiecutter.
