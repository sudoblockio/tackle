# Tackle

[![pypi](https://img.shields.io/pypi/v/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![python](https://img.shields.io/pypi/pyversions/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![codecov](https://codecov.io/gh/robcxyz/tackle-box/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/github/robcxyz/tackle-box?branch=main)
[![main-tests](https://github.com/robcxyz/tackle-box/actions/workflows/main.yml/badge.svg)](https://github.com/robcxyz/tackle-box/actions)

[//]: # (<img align="right" width="80" height="80" src="https://raw.githubusercontent.com/akarsh/akarsh-seggemu-resume/master/akarsh%20seggemu%20resume/Assets/Assets.xcassets/AppIcon.appiconset/Icon-App-60x60%403x.png" alt="Resume application project app icon">)

* [Documentation](https://robcxyz.github.io/tackle-box)
* [Discord](https://discord.gg/7uVUfUVD7K)
* [Slack](https://join.slack.com/t/slack-y748219/shared_invite/zt-1cqreswyd-5qDBE53QlY97mQOI6DhcKw)
* [PyPI](https://pypi.org/project/tackle-box/)
* [BSD License](LICENSE)

Tackle is a language for building modular code generators and declarative CLIs. It can make any config file dynamic with both strong and weakly typed programmable flow control common to a general purpose programming language. Basically you can write a fully functional CLI and Turing-complete program in yaml. It's wild.

> Warning: Tool is in it's very early phases and only now considered stable enough to use. It may never reach 1.x version as, if it gets enough stars, it will be converted to a spec and re-written in rust (ie give it a star if you'd like to see that).

[//]: # (- [Install]&#40;#install&#41;)

[//]: # (- [Hello world]&#40;#hello-world&#41;)

[//]: # (- [Topics]&#40;#topics&#41;)

[//]: # (- [Roadmap]&#40;#roadmap&#41;)

### Install

> Note: tackle can install dependencies on its own. Check [docs](https://robcxyz.github.io/tackle-box/installation#best-installation-method) for advanced installation methods to isolate tackle from your system python.

```shell
python -m venv env && source env/bin/activate
pip install tackle-box
```

### Hello world

To call tackle, create a yaml file and run `tackle hello-world.yaml`.

Simply use the [print](https://robcxyz.github.io/tackle-box/providers/Console/print/) hook.
```yaml
hw->: print Hello world!
```

Which using [jinja templating](https://robcxyz.github.io/tackle-box/jinja) can be called in [four different ways](https://robcxyz.github.io/tackle-box/jinja).
```yaml
words: Hello world!
expanded:
  ->: print
  objects: "{{words}}"
compact->: print {{words}}
jinja_extension->: "{{ print(words) }}"
jinja_filter->: "{{ words | print }}"
```

And can also have interactive [prompt](https://robcxyz.github.io/tackle-box/providers/Prompts/) hooks.
```yaml
name->: input
target:
  ->: select Say hi to who?
  choices:
    - world
    - universe
hello->: print My name is {{name}}. Hello {{target}}!
```

Hooks can have [loops](https://robcxyz.github.io/tackle-box/hook-methods/#loops), [conditionals](https://robcxyz.github.io/tackle-box/hook-methods/#conditionals), and [other base methods](https://robcxyz.github.io/tackle-box/hook-methods/#methods).
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

Hooks can be [written in python](https://robcxyz.github.io/tackle-box/python-hooks/).  
```python
from tackle import BaseHook

class Greeter(BaseHook):
    hook_type: str = "greeter"
    target: str
    args: list = ['target']
    def exec(self):
        print(f"Hello {self.target}")
```

Or new hooks can be [declaratively created](https://robcxyz.github.io/tackle-box/declarative-hooks/) with tackle. Arrows going to the left are basically reusable functions / methods.
```yaml
greeter<-:
  target: str
  args: ['target']
  exec<-:
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

Declarative hooks are strongly typed objects with many [declarative fields](https://robcxyz.github.io/tackle-box/declarative-hooks#input-fields).
```yaml
words<-:
  hi:
    type: str
    regex: ^(Bonjour|Hola|Hello)
  target: str

p->: print {{item}} --for values(words(hi="Hello",target="world!"))
```

Which can have [methods](https://robcxyz.github.io/tackle-box/declarative-hooks#methods) that extend the base.
```yaml
words<-:
  hi: Wadup
  say<-:
    target: str
    exec:
      p->: print {{hi}} {{target}}

p->: words.say --hi Hello --target world!
```

And also support [inheritance](https://robcxyz.github.io/tackle-box/declarative-hooks#extending-hooks).
```yaml
base<-:
  hi:
    default: Hello

words<-:
  extends: base
  say<-:
    target: str
    exec:
      p->: print {{hi}} {{target}}

p->: words.say --target world!
```

> And will later support extending common schemas like OpenAPI, protobuf, and json schema

Hooks and fields can have documentation embedded in them.

```yaml
greeter<-:
  help: Something that greets
  hi:
    default: Yo
    description: Initial greeting.
  target:
    type: str
    description: Thing to greet.
  exec<-:
    p->: print {{hi}} {{target}}
```

> That [will] drive a `help` screen by running `tackle hello-world.yaml --help` -> **Coming soon**

And last, everything can be [imported]() / [called]() remotely from github repos.
```yaml
import-hello_>: import robcxyz/tackle-hello-world
call->: greeter world!
# Or
local-call->: tackle hello-world.yaml
remote-call->: tackle robcxyz/tackle-hello-world --version v0.1.0
```

Creating a web of declarative CLIs.

### Use Cases

- [Code Generation](https://robcxyz.github.io/tackle-box/tutorials/code-generation/)
- [Declarative Utilities]() - wip
- [Kubernetes Manifest Management]() - wip
- [Toolchain Management]() - wip
- [Repo Management]() - wip
- [Home]() - wip

### Topics
- [Writing Tackle Files]() - wip
- [Creating Providers](https://robcxyz.github.io/tackle-box/creating-providers/)
- [Blocks and Flow Control]() - wip
- [Memory Management](https://robcxyz.github.io/tackle-box/memory-management/)
- [Declarative Hooks](https://robcxyz.github.io/tackle-box/declarative-hooks/)
- [Declarative CLIs]() - wip
- [Special Variables]() - wip

### Roadmap

- Declarative schemas
  - json schema
  - openapi
  - protobuf
- Cached providers
- State management

### Contributing

Contributions welcome particularly for additional hooks and suggestions around their interfaces. If contributing to the core parser, please make sure any changes are non-breaking by running tests (`make test`). For writing providers / hooks, please make sure to use the testing conventions laid out in the existing providers whereby the test uses pytest fixtures to change the directory into the test's directory.  This is so the tests can be run from both the root of the project and from within the test directory to facilitate debugging.

### Code of Conduct

Everyone interacting in the tackle-box project's codebases, issue trackers, chat rooms, and mailing lists is expected to follow the [PyPA Code of Conduct](https://www.pypa.io/en/latest/code-of-conduct/).

## Credit

Special thanks to the [cookiecutter](https://github.com/cookiecutter/cookiecutter) community for laying the basis for this project.