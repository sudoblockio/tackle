<img align="right" width="220" height="220" src="https://raw.githubusercontent.com/robcxyz/tackle-box/main/docs/assets/logo-box.png">

# tackle-box


[![pypi](https://img.shields.io/pypi/v/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![python](https://img.shields.io/pypi/pyversions/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![codecov](https://codecov.io/gh/robcxyz/tackle-box/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/github/robcxyz/tackle-box?branch=main)
[![main-tests](https://github.com/robcxyz/tackle-box/actions/workflows/main.yml/badge.svg)](https://github.com/robcxyz/tackle-box/actions)


* [Documentation](https://robcxyz.github.io/tackle-box)
* [Discord](https://discord.gg/7uVUfUVD7K)
* [Slack](https://join.slack.com/t/slack-y748219/shared_invite/zt-1cqreswyd-5qDBE53QlY97mQOI6DhcKw)
* [PyPI](https://pypi.org/project/tackle-box/)
* [BSD License](LICENSE)

Tackle is an experimental language for building modular code generators and declarative CLIs built as a fork of [cookiecutter](https://github.com/cookiecutter/cookiecutter). It can make any config file dynamic with both strong and weakly typed programmable flow control common to a general purpose programming language. Basically you can write a fully functional CLI and Turing-complete program in yaml. It's wild.

### Features

- Makes arbitrary yaml / json / toml [dynamic](https://robcxyz.github.io/tackle-box/hook-methods/)
  - Loops, conditionals, and other base methods
- Ships with a collection of over [100 hooks](https://robcxyz.github.io/tackle-box) to perform a wide variety of specialized actions
  - [Prompt for user inputs](https://robcxyz.github.io/tackle-box)
  - [Generate code from templates](https://robcxyz.github.io/tackle-box/providers/Prompts/)
  - Read and write [yaml](https://robcxyz.github.io/tackle-box/providers/Yaml/) / [toml](https://robcxyz.github.io/tackle-box/providers/Toml/) / [json](https://robcxyz.github.io/tackle-box/providers/Json/) [files](https://robcxyz.github.io/tackle-box/providers/Files/)
  - [Make http calls](https://robcxyz.github.io/tackle-box/providers/Web/)
  - [Run arbitrary system commands](https://robcxyz.github.io/tackle-box/providers/Command/)
  - [Manipulate the context](https://robcxyz.github.io/tackle-box/providers/Context/)
  - [Run other tackle files](https://robcxyz.github.io/tackle-box/providers/Tackle/tackle/)
- Modular design allows creating / importing new hooks a breeze
  - Supports both [python](https://robcxyz.github.io/tackle-box/python-hooks/) and [declarative](https://robcxyz.github.io/tackle-box/declarative-hooks/) hooks which can be called / defined in-line or within jinja templates

### Install

> Note: tackle can install dependencies on its own. Check [docs](https://robcxyz.github.io/tackle-box/installation#best-installation-method) for advanced installation methods to isolate tackle from your system python.

```shell
python -m venv env && source env/bin/activate
pip install tackle-box
```

### Hello world

Check out the [docs](https://robcxyz.github.io/tackle-box/hello-worlds/) for >10 hello worlds that demonstrate the various aspects of the syntax with the simplest one using the [print](https://robcxyz.github.io/tackle-box/providers/Console/print/) hook.

**hello.yaml**
```yaml
hw->: print Hello world!
```

To run, call `tackle hello.yaml`. Can also be [version controlled](https://robcxyz.github.io/tackle-box/creating-providers/) -> [`tackle robcxyz/tackle-hello-world`](https://github.com/robcxyz/tackle-hello-world).

Can also use [loops, conditionals, and other base methods](https://robcxyz.github.io/tackle-box/hook-methods/).

**hello.yaml**
```yaml
words:
  - Hello
  - cruel
  - world!
hw->: print {{item}} --for words --if "item != 'cruel'"
```

New hooks can be [made in python](https://robcxyz.github.io/tackle-box/python-hooks/).

```python
from tackle import BaseHook

class Greeter(BaseHook):
    hook_type: str = "greeter"
    target: str
    args: list = ['target']
    def exec(self):
        print(f"Hello {self.target}")
```

Or can be [defined in a config file](https://robcxyz.github.io/tackle-box/declarative-hooks/).

```yaml
greeter<-:
  target: str
  args: ['target']
  exec<-:
    hi->: print Hello {{target}}
```

And both can be [called in the same way](https://robcxyz.github.io/tackle-box/writing-tackle-files/).

```yaml
hello: world!
compact->: greeter {{hello}}
expanded:
  ->: greeter
  target: "{{hello}}"
jinja_extension->: "{{ greeter(hello) }}"
```

[//]: # (jinja_filter->: "{{ hello | greeter }}")

### Use Cases

- [Code Generation](https://robcxyz.github.io/tackle-box/tutorials/code-generation/)
- [Declarative Utilities]() - wip
- [Infrastructure as code management]() - wip
- [Kubernetes Manifest Management]() - wip
- [Toolchain Management]() - wip
- [Repo Management]() - wip

### Topics
- [Writing Tackle Files](https://robcxyz.github.io/tackle-box/writing-tackle-files/)
- [Python Hooks](https://robcxyz.github.io/tackle-box/python-hooks/)
- [Declarative Hooks](https://robcxyz.github.io/tackle-box/declarative-hooks/)
- [Creating Providers](https://robcxyz.github.io/tackle-box/creating-providers/)
- [Blocks](https://robcxyz.github.io/tackle-box/writing-tackle-files/#blocks) and [Flow Control](https://robcxyz.github.io/tackle-box/hook-methods/)
- [Memory Management](https://robcxyz.github.io/tackle-box/memory-management/)
- [Special Variables](https://robcxyz.github.io/tackle-box/special-variables/)
- [Declarative CLIs]() - wip

### Contributing

Contributions welcome particularly for additional hooks and suggestions around their interfaces. If contributing to the core parser, please make sure any changes are non-breaking by running tests (`make test`). For writing providers / hooks, please make sure to use the testing conventions laid out in the existing providers whereby the test uses pytest fixtures to change the directory into the test's directory.  This is so the tests can be run from both the root of the project and from within the test directory to facilitate debugging.

### Code of Conduct

Everyone interacting in the tackle-box project's codebases, issue trackers, chat rooms, and mailing lists is expected to follow the [PyPA Code of Conduct](https://www.pypa.io/en/latest/code-of-conduct/).

## Credit

Special thanks to the [cookiecutter](https://github.com/cookiecutter/cookiecutter) community for laying the basis for this project.
