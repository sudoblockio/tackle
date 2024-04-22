<img align="right" width="280" height="280" src="https://raw.githubusercontent.com/sudoblockio/tackle/main/docs/assets/logo-box.png">

# tackle

[![pypi](https://img.shields.io/pypi/v/tackle.svg)](https://pypi.python.org/pypi/tackle)
[![python](https://img.shields.io/pypi/pyversions/tackle.svg)](https://pypi.python.org/pypi/tackle)
[![codecov](https://codecov.io/gh/sudoblockio/tackle/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/github/sudoblockio/tackle?branch=main)
[![codeql](https://github.com/sudoblockio/tackle/actions/workflows/codeql.yml/badge.svg)](https://github.com/sudoblockio/tackle/actions/workflows/codeql.yml)

[//]: # ([![main-tests]&#40;https://github.com/sudoblockio/tackle/actions/workflows/main.yml/badge.svg&#41;]&#40;https://github.com/sudoblockio/tackle/actions&#41;)

* [Documentation](https://sudoblockio.github.io/tackle)
* [Discord](https://discord.gg/7uVUfUVD7K)
* [PyPI](https://pypi.org/project/tackle/)
* [BSD License](LICENSE)

[//]: # (* [Slack]&#40;https://join.slack.com/t/slack-y748219/shared_invite/zt-1cqreswyd-5qDBE53QlY97mQOI6DhcKw&#41;)

Tackle is a multi-paradigm configuration language for building modular code generators, schema validators, and declarative CLIs. Built as a fork of [cookiecutter](https://github.com/cookiecutter/cookiecutter) and on top of [pydantic](), it can make any config file into a CLI with both strong and weakly typed programmable flow control common to a general purpose programming language. Comparable with [CUE](), [Jsonnet](), and [Dhall](),  with more features and cleaner syntax, you can write a fully functional Turing-complete program out of a json/yaml/toml file. It's wild.

**With tackle, you can build:**
- Modular code generators / repo scaffolding tools that can be updated over time
- Interactive glue code for infrastructure-as-code deployment strategies
- Validate complex schemas composing them with strongly typed objects
- Generic utilities like SSH helpers and dotfile managers
- Combinations of all of the above and anything else you can think of

[//]: # (- Declarative makefile alternatives for advanced toolchain management)

> WARNING: Tackle is still in alpha so expect some changes in the future.

### Features

- Multi-paradigm
  - Create strong and weakly typed objects with custom validation logic
  - Objects can have methods and be extended through inheritance
  - Compose objects to create nested validation structures

- Makes arbitrary yaml / json / toml [dynamic](https://sudoblockio.github.io/tackle/hook-methods/)
  - Embed loops, conditionals, and other custom flow control logic
  - Self documenting CLI to call tackle from command line
- Ships with a collection of over [100 hooks](https://sudoblockio.github.io/tackle) that act like plugins within your config file
  - [Prompt user for inputs](https://sudoblockio.github.io/tackle)
  - [Generate code from templates](https://sudoblockio.github.io/tackle/providers/Generate/)
  - Read and write [yaml](https://sudoblockio.github.io/tackle/providers/Yaml/) / [toml](https://sudoblockio.github.io/tackle/providers/Toml/) / [json](https://sudoblockio.github.io/tackle/providers/Json/) [files](https://sudoblockio.github.io/tackle/providers/Files/)
  - [Make http calls](https://sudoblockio.github.io/tackle/providers/Web/)
  - [Run arbitrary system commands](https://sudoblockio.github.io/tackle/providers/Command/)
  - [Manipulate the context](https://sudoblockio.github.io/tackle/providers/Context/)
  - [Run other tackle files](https://sudoblockio.github.io/tackle/providers/Tackle/tackle/)
- Modular design allows creating / importing new hooks easy
  - Supports both [python](https://sudoblockio.github.io/tackle/python-hooks/) and [declarative](https://sudoblockio.github.io/tackle/declarative-hooks/) hooks which can be imported / called / defined in-line or within jinja templates
  - Hooks can be composed / inherited with / from other hooks allowing complex objects to be validated and operated against
- Expressive macro system creating intuitive interfaces

### Install

> Note: tackle can install dependencies on its own. Check [docs](https://sudoblockio.github.io/tackle/installation#best-installation-method) for advanced installation methods to isolate tackle from your system python.

```shell
python -m venv env && source env/bin/activate
pip install tackle
```

**Quick Demo:** `tackle sudoblockio/tackle-hello-world`

### Hello world

Check out the [docs](https://sudoblockio.github.io/tackle/hello-worlds/) for >10 hello worlds that demonstrate the various aspects of the syntax with the simplest one using the [print](https://sudoblockio.github.io/tackle/providers/Console/print/) hook, one of [>100 hooks](https://sudoblockio.github.io/tackle/providers/Collections/).

**hello.yaml**
```yaml
# Any time a key ends with `->`, we are calling a hook
any key->: print Hello world!
# `print` is a hook which can also be used as a special key
print->: Hello world!
```

To run, call `tackle hello.yaml`. Can also be [version controlled](https://sudoblockio.github.io/tackle/creating-providers/) -> [`tackle sudoblockio/tackle-hello-world`](https://github.com/sudoblockio/tackle-hello-world).

Can also use [loops, conditionals, and other base methods like try / except](https://sudoblockio.github.io/tackle/hook-methods/).

**hello.yaml**
```yaml
the:
  words:
    - Hello
    - cruel
    - world!
# Compact one liners
one liner->: print {{i}} --for i in the.words --if i != 'cruel'
# Which can also be expressed in multiple lines
multiple lines:
  ->: print
  objects: {{item}}
  for:
    - Hello
    - cruel
    - world!
  if: item != 'cruel'
# Or combinations of the above
combination:
  ->: print {{i}}
  for: i in ['Hello','world!']
# As a special key
print->: Hello {{i}} --for i in the.words
# Or through jinja rendering
with rendering->: "{{print('Hello','world!'}}"
```

New hooks can be [made in python](https://sudoblockio.github.io/tackle/python-hooks/) which under the hood is a [pydantic](https://github.com/pydantic/pydantic) model.

**.hooks/hello.py**

```python
from tackle import BaseHook


class Greeter(BaseHook):
  hook_name = "greeter"
  target: str

  hook_args = ['target']

  def exec(self):
    expression = f"Hello {self.target}"
    print(expression)
    return expression
```

Or can be [defined inline within your tackle file, imported remotely, or in a `hooks` directory.](https://sudoblockio.github.io/tackle/declarative-hooks/).

**.hooks/hello.yaml**
```yaml
# Keys ending with `<-` mean we are creating a hook / method
greeter<-:
  target: str
  args: ['target']
  exec<-:
    expression->: var Hello {{target}}  # var hook renders variables
    p->: print {{expression}}
  return: expression
```

And both can be [called the same way](https://sudoblockio.github.io/tackle/writing-tackle-files/).

**tackle.yaml**
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

Hooks are also [callable from the command line](https://sudoblockio.github.io/tackle/declarative-cli/):

```shell
tackle hello.yaml greeter --target world!
# Or from a github repo
tackle sudoblockio/tackle-hello-world greeter --target world!
```

Documentation can be embedded into the hooks.

**hello.yaml**
```yaml
<-:
  help: This is the default hook
  target:
    type: list[greeter]
    default->: input
    description: The thing to say hello to
  exec<-:
    greeting->: select Who to greet? --choices ['world',target]
    hi->: greeter --target {{greeting}}
  greeting-method<-:
    help: A method that greets
    # ... Greeting options / logic
    extends: greeter
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

Hooks can be imported [within a tackle provider](https://sudoblockio.github.io/tackle/declarative-cli/#importing-hooks) or [through hooks](https://sudoblockio.github.io/tackle/providers/Tackle/import/), [linked](https://sudoblockio.github.io/tackle/providers/Tackle/tackle/), and/or combined with [inheritance](https://sudoblockio.github.io/tackle/declarative-hooks/#extending-hooks) or [composition](https://sudoblockio.github.io/tackle/declarative-hooks/#extending-hooks) creating a web of CLIs.

### Use Cases

- [Code Generation](https://sudoblockio.github.io/tackle/tutorials/code-generation/)

**WIP Tutorials**

- Declarative Utilities
- Infrastructure-as-Code Management
- Kubernetes Manifest Management
- Toolchain Management

[//]: # (- [Repo Management]&#40;&#41; - wip)

### Topics

- [Writing Tackle Files](https://sudoblockio.github.io/tackle/writing-tackle-files/)
- [Creating Providers](https://sudoblockio.github.io/tackle/creating-providers/)
- [Python Hooks](https://sudoblockio.github.io/tackle/python-hooks/)
- [Declarative Hooks](https://sudoblockio.github.io/tackle/declarative-hooks/)
- [Blocks](https://sudoblockio.github.io/tackle/writing-tackle-files/#blocks) and [Flow Control](https://sudoblockio.github.io/tackle/hook-methods/)
- [Memory Management](https://sudoblockio.github.io/tackle/memory-management/)
- [Special Variables](https://sudoblockio.github.io/tackle/special-variables/)
- [Declarative CLIs](https://sudoblockio.github.io/tackle/declarative-cli/)

### Known Issues

- **Windows Support**
  - tackle is lacking some windows support as shown in the [failed tests](https://github.com/sudoblockio/tackle/actions/workflows/main-windows.yml). If you are a windows user, it is highly recommended to use WSL. **Please get in touch** if you are motivated to fix these tests to make tackle fully cross-platform. It probably isn't that hard to fix them as they mostly are due to differences in how windows handles paths.
- **Whitespaces**
  - tackle relies heavily on parsing based on whitespaces which if you are not careful can easily bite you. Whenever you need to have some whitespaces preserved, make sure to quote the entire expression. Future work will be put in to overhaul the [regex based parser](https://github.com/sudoblockio/tackle/blob/main/tackle/utils/command.py#L52) with a PEG parser or AST.

### Contributing

```shell
git clone
cd tackle
make  # Creates and sources virtualenv
tackle --version  # Stable version installed from pypi for managing tackle
tackle test  # Run tests with tackle
make test  # Alternatively run with make
```
Contributions are welcome but please be advised of the following notes.

- This project uses [conventional commits](https://www.conventionalcommits.org/) which generates the [changelog](./CHANGELOG.md) with [release-please-action](https://github.com/google-github-actions/release-please-action) in the [release](https://github.com/sudoblockio/tackle/blob/main/.github/workflows/release.yml) CI workflow. If commits have been made outside of this convention they will be squashed accordingly.
- For making changes to providers, please include test coverage using the existing fixtures and patterns from prior tests or communicate any suggestions that deviate from this style. It definitely can be improved but consistency is more important than making directed improvements. Tests should be runnable from the test's directory and via `tackle test`.
- For making changes to the core parser, please create a proposal first outlining your suggestions with examples before spending time working on code.

It is very easy to create new providers / hooks with tackle. Over time, it will adopt the same import pattern of what Ansible does where all provider / hooks (modules) are stored in version controlled locations. In the meantime, please feel free to contribute to this repository for hooks that have general applicability with no dependencies in the [providers](providers) directory or  or create your own hooks in other repositories that are more bespoke / opinionated in nature.

### Future Directions

It was always the intention for tackle to be re-written in some kind of compiled language and if the language gets some decent traction, that will be done. Goals will be:

- Improved parsing performance - tackle should be [blazing fast](https://www.youtube.com/watch?v=Z0GX2mTUtfo)
- Overhaul of string parsers - should be token based exposing more language features
- Improved linking cabablities -
- Ship as a single binary - Not only the tackle interpreter, but an entire tackle provider with linked dependencies  
- Compiled to WASM - Make tackle usable from any language
- A registry - This is a no brainer when you have a language with modular charectoristics

Instead, the intention will be to integrate Mojo's language features to allow binaries to be compiled from tackle scripts and providers. This will be a major challenge but the benefits will be worth it. Theoretically, tackle could be very fast when it make this switch and useful in a variety of other interesting applications.

### Code of Conduct

Everyone interacting in the tackle project's codebases, issue trackers, chat rooms, and mailing lists is expected to follow the [PyPA Code of Conduct](https://www.pypa.io/en/latest/code-of-conduct/).

## Credit

Special thanks to the [cookiecutter](https://github.com/cookiecutter/cookiecutter) community for laying the basis for this project.
