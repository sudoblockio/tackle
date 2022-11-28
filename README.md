<img align="right" width="280" height="280" src="https://raw.githubusercontent.com/robcxyz/tackle/main/docs/assets/logo-box.png">

# tackle

[![pypi](https://img.shields.io/pypi/v/tackle.svg)](https://pypi.python.org/pypi/tackle)
[![python](https://img.shields.io/pypi/pyversions/tackle.svg)](https://pypi.python.org/pypi/tackle)
[![codecov](https://codecov.io/gh/robcxyz/tackle/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/github/robcxyz/tackle?branch=main)
[![codeql](https://github.com/robcxyz/tackle/actions/workflows/codeql.yml/badge.svg)](https://github.com/robcxyz/tackle/actions/workflows/codeql.yml)
[![Foresight Docs](https://api-public.service.runforesight.com/api/v1/badge/success?repoId=4abde40b-565a-4557-afc0-983461857bb4)](https://docs.runforesight.com/)
[![Foresight Docs](https://api-public.service.runforesight.com/api/v1/badge/test?repoId=4abde40b-565a-4557-afc0-983461857bb4)](https://docs.runforesight.com/)
[![Foresight Docs](https://api-public.service.runforesight.com/api/v1/badge/utilization?repoId=4abde40b-565a-4557-afc0-983461857bb4)](https://docs.runforesight.com/)

[//]: # ([![main-tests]&#40;https://github.com/robcxyz/tackle/actions/workflows/main.yml/badge.svg&#41;]&#40;https://github.com/robcxyz/tackle/actions&#41;)

* [Documentation](https://robcxyz.github.io/tackle)
* [Discord](https://discord.gg/7uVUfUVD7K)
* [PyPI](https://pypi.org/project/tackle/)
* [BSD License](LICENSE)

[//]: # (* [Slack]&#40;https://join.slack.com/t/slack-y748219/shared_invite/zt-1cqreswyd-5qDBE53QlY97mQOI6DhcKw&#41;)

Tackle is an experimental DSL for building modular code generators and declarative CLIs. Built as a fork of [cookiecutter](https://github.com/cookiecutter/cookiecutter), it can make any config file dynamic or into a CLI with both strong and weakly typed programmable flow control common to a general purpose programming language. Basically you can write a fully functional Turing-complete program out of a config file. It's wild.

**With tackle, you can build:**
- Modular code generators / repo scaffolding tools that can be updated over time
- Interactive glue code for infrastructure-as-code deployment strategies
- Generic utilities like SSH registries and dotfile managers
- Combinations of all of the above and anything else you can think of

[//]: # (- Declarative makefile alternatives for advanced toolchain management)

> If this project gets enough adoption / stars, it will be re-written in a compiled language. 

### Features

- Makes arbitrary yaml / json / toml [dynamic](https://robcxyz.github.io/tackle/hook-methods/)
  - Embed loops, conditionals, and other custom logic
  - Self documenting CLI to call logic
- Ships with a collection of over [100 hooks](https://robcxyz.github.io/tackle) that act like plugins within your config file
  - [Prompt user for inputs](https://robcxyz.github.io/tackle)
  - [Generate code from templates](https://robcxyz.github.io/tackle/providers/Generate/)
  - Read and write [yaml](https://robcxyz.github.io/tackle/providers/Yaml/) / [toml](https://robcxyz.github.io/tackle/providers/Toml/) / [json](https://robcxyz.github.io/tackle/providers/Json/) [files](https://robcxyz.github.io/tackle/providers/Files/)
  - [Make http calls](https://robcxyz.github.io/tackle/providers/Web/)
  - [Run arbitrary system commands](https://robcxyz.github.io/tackle/providers/Command/)
  - [Manipulate the context](https://robcxyz.github.io/tackle/providers/Context/)
  - [Run other tackle files](https://robcxyz.github.io/tackle/providers/Tackle/tackle/)
- Modular design allows creating / importing new hooks easy
  - Supports both [python](https://robcxyz.github.io/tackle/python-hooks/) and [declarative](https://robcxyz.github.io/tackle/declarative-hooks/) hooks which can be imported / called / defined in-line or within jinja templates

### Install

> Note: tackle can install dependencies on its own. Check [docs](https://robcxyz.github.io/tackle/installation#best-installation-method) for advanced installation methods to isolate tackle from your system python.

```shell
python -m venv env && source env/bin/activate
pip install tackle
```

**Quick Demo:** `tackle robcxyz/tackle-hello-world`

### Hello world

Check out the [docs](https://robcxyz.github.io/tackle/hello-worlds/) for >10 hello worlds that demonstrate the various aspects of the syntax with the simplest one using the [print](https://robcxyz.github.io/tackle/providers/Console/print/) hook, one of [>100 hooks](https://robcxyz.github.io/tackle/installation#best-installation-method).

**hello.yaml**
```yaml
# Any time a key ends with `->`, we are calling a hook
hw->: print Hello world!
```

To run, call `tackle hello.yaml`. Can also be [version controlled](https://robcxyz.github.io/tackle/creating-providers/) -> [`tackle robcxyz/tackle-hello-world`](https://github.com/robcxyz/tackle-hello-world).

Can also use [loops, conditionals, and other base methods](https://robcxyz.github.io/tackle/hook-methods/).

**hello.yaml**
```yaml
the:
  words:
    - Hello
    - cruel
    - world!
one liner->: print --for the.words --if "item != 'cruel'" {{item}}
multiple lines:
  ->: print
  for:
    - Hello
    - world!
# Or combinations of the above with other methods like try/except
```

New hooks can be [made in python](https://robcxyz.github.io/tackle/python-hooks/)
 which under the hood is a [pydantic](https://github.com/pydantic/pydantic) model.

```python
from tackle import BaseHook

class Greeter(BaseHook):
    hook_type: str = "greeter"
    target: str
    args: list = ['target']
    def exec(self):
      expression = f"Hello {self.target}"
      print(expression)
      return expression
```

Or can be [defined inline within your tackle file.](https://robcxyz.github.io/tackle/declarative-hooks/).

```yaml
# Keys ending with `<-` mean we are creating a hook / method
greeter<-:
  target: str
  args: ['target']
  exec<-:
    expression: Hello {{target}}
    p->: print {{expression}}
  return: expression
```

And both can be [called in the same way](https://robcxyz.github.io/tackle/writing-tackle-files/).

```yaml
hello: world!
With a flag->: greeter --target {{hello}}
Target in argument->: greeter {{hello}}
Expanded fields:
  ->: greeter
  target: {{hello}}
Jinja template->: {{ greeter(hello) }}
# Or combinations jinja and compact / expanded hooks allowing chaining of hook calls.  
```

With the declarative hooks being callable from the command line:

```shell
tackle hello.yaml --target world!
# Or from a github repo
tackle robcxyz/tackle-hello-world --checkout v0.1.0
```

Documentation can be embedded into the hooks.

```yaml
<-:
  help: This is the default hook
  target:
    type: str
    default->: input
    description: The thing to say hello to
  exec<-:
    greeting->: select Who to greet? --choices ['world',target]
    hi->: greeter --target {{greeting}}
  greeting-method<-:
    help: A method that greets
    # ... Greeting options / logic
greeter<-:
  help: A reusable greeter object
  target: str
  exec<-:
    hi->: print Hello {{target}}
```

Which when running `tackle hello.yaml help` produces its own help screen.

```text
usage: tackle hello.yaml [--target]

This is the default hook

options:
    --target [str] The thing to say hello to
methods:
    greeting-method     A method that greets
    greeter     A reusable greeter object
```

Hooks can be imported, linked, and/or combined creating a web of CLIs.

### Use Cases

- [Code Generation](https://robcxyz.github.io/tackle/tutorials/code-generation/)

**WIP Tutorials**

- [Declarative Utilities]()
- [Infrastructure-as-Code Management]()
- [Kubernetes Manifest Management]()
- [Toolchain Management]()

[//]: # (- [Repo Management]&#40;&#41; - wip)

### Topics

- [Writing Tackle Files](https://robcxyz.github.io/tackle/writing-tackle-files/)
- [Creating Providers](https://robcxyz.github.io/tackle/creating-providers/)
- [Python Hooks](https://robcxyz.github.io/tackle/python-hooks/)
- [Declarative Hooks](https://robcxyz.github.io/tackle/declarative-hooks/)
- [Blocks](https://robcxyz.github.io/tackle/writing-tackle-files/#blocks) and [Flow Control](https://robcxyz.github.io/tackle/hook-methods/)
- [Memory Management](https://robcxyz.github.io/tackle/memory-management/)
- [Special Variables](https://robcxyz.github.io/tackle/special-variables/)
- [Declarative CLIs](https://robcxyz.github.io/tackle/declarative-cli/)

### Contributing

Contributions are welcome but please be advised of the following notes.

- This project uses [conventional commits](https://www.conventionalcommits.org/) which generates the [changelog](./CHANGELOG.md) with [release-please-action]() in the [release]() CI workflow. If commits have been made outside of this convention they will be squashed accordingly.
- For making changes to providers, please include test coverage using the existing fixtures and patterns from prior tests or communicate any suggestions that deviate from this style. Tests should be runnable from the test's directory and via `make test`.
- For making changes to the core parser, please create a proposal first outlining your suggestions with examples before spending time working on code.

It is very easy to create new providers / hooks with tackle. Over time, it will adopt the same import pattern of what Ansible does where all provider / hooks (modules) are stored in version controlled locations. In the meantime, please feel free to contribute to this repository for hooks that have general applicability or create your own hooks in other repositories that are more bespoke / opinionated in nature.

### Code of Conduct

Everyone interacting in the tackle project's codebases, issue trackers, chat rooms, and mailing lists is expected to follow the [PyPA Code of Conduct](https://www.pypa.io/en/latest/code-of-conduct/).

## Credit

Special thanks to the [cookiecutter](https://github.com/cookiecutter/cookiecutter) community for laying the basis for this project.
