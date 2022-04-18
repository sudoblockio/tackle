# Tackle

[![pypi](https://img.shields.io/pypi/v/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![python](https://img.shields.io/pypi/pyversions/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![codecov](https://codecov.io/gh/robcxyz/tackle-box/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/github/robcxyz/tackle-box?branch=main)
[![main-tests](https://github.com/robcxyz/tackle-box/actions/workflows/main.yml/badge.svg)](https://github.com/robcxyz/tackle-box/actions)

* [Documentation](https://robcxyz.github.io/tackle-box)
* [PyPI](https://pypi.org/project/tackle-box/)
* [BSD License](LICENSE)

Tackle box is a language for making modular declarative CLIs. Make any yaml/json configuration file dynamic/callable with turing complete flow control common to any general purpose programming language.

> Warning: Language is in it's very early phases and only now considered stable enough to use. It may never reach 1.x version as, if it gets enough stars, it will be converted to a spec and re-written in rust (ie give it a star if you'd like to see that).

- Install
- Use Cases
- Hello world
- Advanced Topics
- Contributing

### Install

Note: tackle can install dependencies on its own. Check [docs]() for advanced installation methods to isolate tackle from your system python.

```shell
python -m venv env
pip install tackle-box
```

### Use Cases

- [Modular code generation]() - wip
- [Kubernetes management]() - wip
- [Declarative toolchains]() - wip
- [Declarative utilities]() - wip

### Hello worlds

To call tackle, create a yaml file and run `tackle hello-world.yaml`.

Use the [print](https://robcxyz.github.io/tackle-box/providers/Console/print/) hook.
```yaml
hw->: print Hello world!
```

Using [jinja templating](), hooks can be called in [four different ways]().
```yaml
words: Hello world!
expanded:
  ->: print
  objects: "{{words}}"
compact->: print {{words}}
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

Hooks can have for [loops](https://robcxyz.github.io/tackle-box/hook-methods/#loops), [conditionals](https://robcxyz.github.io/tackle-box/hook-methods/#conditionals), and [other base methods](https://robcxyz.github.io/tackle-box/hook-methods/#methods).
```yaml
words:
  - Hello
  - cruel
  - world!
expanded:
  ->: print {{item}}
  for: words
  if: item != 'cruel'
compact->: print {{item}} --for words --if "item != 'cruel'"
```

Hooks can be [written in python]().
```python
from tackle import BaseHook

class Greeter(BaseHook):
    hook_type: str = "greeter"
    target: str
    args: list = ['target']
    def exec(self):
        print(f"Hello {self.target}")
```

Or new hooks can be [declaratively created]() with tackle.
```yaml
greeter<-:
  help: A thing that says hi!
  target: str
  args:
    - target
  exec:
    hi->: print Hello {{target}}
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

Or can be imported / called remotely.
```yaml
local-call->: tackle hello-world.yaml
remote-call->: tackle robcxyz/tackle-hello-world
# Or
import-hello_>: import robcxyz/tackle-hello-world
call->: greeter world!
```

Creating a web of declarative CLIs.

### Topics
- [Writing Tackle Files](https://robcxyz.github.io/tackle-box/writing-tackle-files/)
- [Creating Providers](https://robcxyz.github.io/tackle-box/creating-providers/)
- [Blocks and Flow Control]()
- [Memory Management]()
- [Declarative CLIs]()
- [Declarative Hooks]()
- [Special Variables]()

### Roadmap

- Declarative hook inheritance
- Declarative schemas
- Declarative methods
- Cached providers
- State management

### Code of Conduct

Everyone interacting in the tackle-box project's codebases, issue trackers, chat rooms, and mailing lists is expected to follow the [PyPA Code of Conduct](https://www.pypa.io/en/latest/code-of-conduct/).

## Credit

Special thanks to the [cookiecutter](https://github.com/cookiecutter/cookiecutter) community for laying the basis for this project.
