# Tackle

[![pypi](https://img.shields.io/pypi/v/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![python](https://img.shields.io/pypi/pyversions/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![codecov](https://codecov.io/gh/robcxyz/tackle-box/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/github/robcxyz/tackle-box?branch=main)
[![main-tests](https://github.com/robcxyz/tackle-box/actions/workflows/main.yml/badge.svg)](https://github.com/robcxyz/tackle-box/actions)

* [Documentation](https://robcxyz.github.io/tackle-box) (WIP)
* [PyPI](https://pypi.org/project/tackle-box/)
* [BSD License](LICENSE)

[//]: # (Tackle box is a DSL for turning static configuration files into dynamic workflows. Tool is plugins based and can easily be extended by writing additional hooks or importing external providers.)

[//]: # ()
[//]: # (Tackle box is a programmable configuration language and declarative CLI written in yaml and extended with importable providers. Tackle parsers arbitrary configuration files and reacts to keys ending in arrows &#40;'->'/'<-'&#41; to take special actions. Make any configuration file dynamic, callable, or simply into a CLI with tackle.)

[//]: # ()
[//]: # (Tackle is a modular programmable configuration language and declarative CLI that can make any yaml/json file dynamic/callable.)

Tackle is a modular programmable configuration language and declarative CLI. It can make any yaml/json configuration file dynamic/callable with flow control common to any general purpose programming language.

> Warning: Language is very usable but in its early phases. It may never reach 1.x version as, if it gets enough github stars, it will be converted to a spec and re-written in rust (ie give it a star if you'd like to see that).

- Install
- Use Cases
- Hello world
- Advanced Topics
- Contributing

### Install

Note: tackle can install dependencies on its own

```shell
python -m venv env
pip install tackle-box
```

### Use Cases

- [Modular code generation]()
- [Kubernetes management]()
- [Declarative toolchains]()
- [Declarative utilities]()

### Hello worlds

To call tackle, simply create a yaml file and call it with `tackle hello-world.yaml`.

Use the [print]() hook.
```yaml
hw->: print Hello world!
```

Using [jinja templating](), hooks can be called in [four different ways]().
```yaml
words: Hello world!
compact->: print {{words}}
expanded:
  ->: print
  objects: "{{words}}"
jinja_extension->: "{{ print(words) }}"
jinja_filter->: "{{ words | print }}"
```

Interactive example with [prompt]() hooks.
```yaml
name->: input
target:
  ->: select Say hi to who?
  choices:
    - world
    - universe
hello->: print My name is {{name}}. Hello {{target}}!
```

Hooks can have for [loops](), [conditionals](), and [other base methods]().
```yaml
words:
  - Hello
  - cruel
  - world!
compact->: print {{item}} --for words --if "item != 'cruel'"
expanded:
  ->: print {{item}}
  for: words
  if: item != 'cruel'
```

New hooks can be [declaratively created]() with tackle.
```yaml
greeter<-:
  help: A thing that says hi!
  target: str
  args:
    - target
  exec:
    hi->: print Hello {{target}}
```

Or hooks can be [written in python]().
```python
from tackle import BaseHook

class Greeter(BaseHook):
    hook_type: str = "greeter"
    target: str
    args: list = ['target']
    def exec(self):
        print(f"Hello {self.target}")
```

And both can be called in the same way.
```yaml
hello: world!
compact->: greeter {{hello}}
expanded:
  ->: greeter
  target: "{{hello}}"
jinja_extension->: "{{ greeter(hello) }}"
jinja_filter->: "{{ hello | greeter }}"
```

Hooks and other tackle files can be imported and / or called.
```yaml
local-call->: tackle hello-world.yaml
remote-call->: tackle robcxyz/tackle-hello-world
# Or
import-hello_>: import robcxyz/tackle-hello-world
call->: greeter world!
```

Creating a web of declarative CLIs.

### Advanced Topics

- Blocks and Flow Control
- Declarative CLIs
- Imperitive vs Declarative Hooks
- Public / Private Hooks
- Special Variables


### Road Map

The main challenge with this project is going to be reaching a stable syntax that people can reliably build on. Until that happens any feedback is welcome both on the core parsing logic or hook interfaces. A place outside of github issues will be made to better accommodate those conversations.

### Code of Conduct

Everyone interacting in the Cookiecutter project's codebases, issue trackers,
chat rooms, and mailing lists is expected to follow the
[PyPA Code of Conduct](https://www.pypa.io/en/latest/code-of-conduct/).

## Credit

Special thanks to the [cookiecutter](https://github.com/cookiecutter/cookiecutter) community for laying the basis for this project.
