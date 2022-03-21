# Tackle

[![pypi](https://img.shields.io/pypi/v/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![python](https://img.shields.io/pypi/pyversions/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![codecov](https://codecov.io/gh/robcxyz/tackle-box/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/github/robcxyz/tackle-box?branch=main)
[![main-tests](https://github.com/robcxyz/tackle-box/actions/workflows/main.yml/badge.svg)](https://github.com/robcxyz/tackle-box/actions)

* [Documentation](https://robcxyz.github.io/tackle-box) (WIP)
* [GitHub](https://github.com/robcxyz/tackle-box)
* [PyPI](https://pypi.org/project/tackle-box/)
* [BSD License](LICENSE)

Tackle box is a DSL for turning static configuration files into dynamic workflows. Tool is plugins based and can easily be extended by writing additional hooks or importing external providers.

Tackle box is a programmable configuration language and declarative CLI written in yaml and extended with importable providers. Tackle parsers arbitrary configuration files and reacts to keys ending in arrows ('->'/'<-') to take special actions. Make any configuration file dynamic, callable, or simply into a CLI with tackle.

Tackle is a modular programmable configuration language and declarative CLI that can make any yaml/json file dynamic/callable.

Tackle is a modular programmable configuration language and declarative CLI. Make any yaml/json file dynamic/callable.

> Warning: Language is very usable but in its early phases. It may never reach 1.x version as if it gets enough stars, it will be converted to a spec and re-written in rust.  

- Install
- Use Cases
- Hello worlds

### Install

```shell
pip install tackle-box
```

### Use Cases

- [Modular code generation]()
- [Kubernetes management]()
- [Declarative utilities]()

### Hello worlds

To call tackle, simply create a yaml file and call it with `tackle hello-world.yaml`

Use the [print]() hook.
```yaml
p->: print Hello world!
```

Using [jinja templating](), hooks can be called in [four different ways]().
```yaml
hello: Hello world!
jinja_extension->: "{{ print(hello) }}"
jinja_filter->: "{{ hello | print }}"
compact->: print {{hello}}
expanded:
  ->: print
  object: "{{hello}}"
```

Interactive example with [prompt]() hooks.
```yaml
name->: input
target:
  ->: select Say hi to who?
  choices:
    - world
    - universe
hello_>: print My name is {{name}}. Hello {{target}}!
```

Hooks can have for [loops](), [conditionals](), and [other base methods]().
```yaml
words:
  - Hello
  - cruel
  - world!
hello_>: print {{item}} --for words --if "item != 'cruel'"
```

New hooks can be [declaratively created]() with tackle.
```yaml
greeter<-:
  help: A thing that says hi!
  fields:
    target: str
  exec:
    hi->: print Hello {{target}}
  args:
    - target
```

Or hooks can be [written in python]().
```python
from tackle import BaseHook

class Greeter(BaseHook):
    hook_type: str = "greeter"
    target: str
    _args: list = ['target']

    def exec(self):
        print(f"Hello {self.target}")
```

```yaml
say_hi->: greeter world!
```

Hooks and other tackle files can be imported and / or called.

```yaml
local-call->: tackle hello-world.yaml
remote-call->: tackle robcxyz/tackle-hello-world
# Or
import-hello->: import robcxyz/tackle-hello-world
call->: greeter world!
```

### Demo

```shell
pip3 install tackle-box

# Create a new provider in one minute
tackle robcxyz/tackle-provider

# Push to github and now you can call it directly
tackle <your GH username>/<tackle-your-provider>

# Or alternatively create a tackle file
echo '
name->: input What is your name?
print->: print Hi {{name}}, lets make a provider now!
call->: tackle robcxyz/tackle-provider
' > tackle.yaml
tackle
```

### Features

- Modular: New providers / hooks can be created or imported remotely
- Declarative: Everything is in yaml with easy to use interfaces
- Turing complete: Loops, conditionals and branching is supported
- Lean: Tackle box has only 4 dependencies - core logic <1k LOC

### Usage

Tackle-box in its simplest form is a structured data parser taking in arbitrary yaml or json and only applying logic with keys ending in an arrow (ie '->'). By default, tackle looks for a `tackle.yaml` file in the target location which is parsed sequentially with each key / value or item in a list traversed, parsed, and rendered on hook calls indicated by an arrow (`->`). Tackle box ships with ~70 hooks to do basic prompting / code generation / system operations but can easily be extended by writing additional hooks or importing other providers.

### Provider Structure

For instance given the following directory structure:

```
├── hooks
│ └── stuff.py
└── tackle.yaml
```

With **`stuff.py`** looking like:

```python
from tackle import BaseHook

class Stuff(BaseHook):
    hook_type: str = "do-stuff"
    things: str
    _args: list = ['things']

    def exec(self):
        return self.things.title()
```

One could write a **`tackle.yaml`** that looks like this:

```yaml
compact->: do-stuff a string
expanded:
  if: compact == 'A String'
  ->: do-stuff
  things: "{{compact}} That Renders!"
```

Which if you call `tackle` in that directory would result in the following context:

```yaml
compact: A String
expanded: A String That Renders!
```

Which you can use to then generate code, print out to file, or do any number of custom actions with additional hook calls or calls to other tackle providers. For instance if you wanted to use it in another tackle provider and generate code, you would use:

```yaml
remote_call->: tackle robcxyz/tackle-do-stuff  # Fictitious repo
gen->: generate path/to/jinja/templates output/path
```

Which would result in the same context embedded under the `remote_call` key and would be used to generate files / directories of templates to the output path.

### Road Map

The main challenge with this project is going to be reaching a stable syntax that people can reliably build on. Until that happens any feedback is welcome both on the core parsing logic or hook interfaces. A place outside of github issues will be made to better accommodate those conversations.

### Code of Conduct

Everyone interacting in the Cookiecutter project's codebases, issue trackers,
chat rooms, and mailing lists is expected to follow the
[PyPA Code of Conduct](https://www.pypa.io/en/latest/code-of-conduct/).

## Credit

Special thanks to the [cookiecutter](https://github.com/cookiecutter/cookiecutter) community for laying the basis for this project.
