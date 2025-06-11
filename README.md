<img align="right" width="280" height="280" src="https://raw.githubusercontent.com/sudoblockio/tackle/main/docs/assets/logo-box.png">

# tackle

[![pypi](https://img.shields.io/pypi/v/tackle.svg)](https://pypi.python.org/pypi/tackle)
[![python](https://img.shields.io/pypi/pyversions/tackle.svg)](https://pypi.python.org/pypi/tackle)
[![codecov](https://codecov.io/gh/sudoblockio/tackle/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/github/sudoblockio/tackle?branch=main)

[//]: # ([![codeql]&#40;https://github.com/sudoblockio/tackle/actions/workflows/codeql.yml/badge.svg&#41;]&#40;https://github.com/sudoblockio/tackle/actions/workflows/codeql.yml&#41;)
[//]: # ([![main-tests]&#40;https://github.com/sudoblockio/tackle/actions/workflows/main.yml/badge.svg&#41;]&#40;https://github.com/sudoblockio/tackle/actions&#41;)
[//]: # (* [Discord]&#40;https://discord.gg/7uVUfUVD7K&#41;)

* [Documentation](https://sudoblockio.github.io/tackle)
* [PyPI](https://pypi.org/project/tackle/)

tackle is an experimental DSL built as a fork of [cookiecutter](https://github.com/cookiecutter/cookiecutter) written in documents such as json, yaml, or toml with primitives of a general purpose programming language including functions, structs, methods, and types with rich control flow. It turns a config file into self documenting CLI in a concise declarative syntax.

Core to the language is the notion of a `hook` which is a [pydantic](https://github.com/pydantic/pydantic) [BaseModel](https://docs.pydantic.dev/latest/api/base_model/) under the hood. These hooks can be created, called, or combined in documents and / or python with inheritance and composition. Tackle ships with over 100 native hooks to perform rudimentary tasks from prompting users for CLI inputs, reading / manipulating / writing data to and from files, to rendering templates for code generation / schema translations.

Major syntax changes will be made before the language is officially released and thus using the language is discouraged without reaching out first by leaving issues in this repo. A formal spec is under active development but has sort of taken the back seat while Rob is working on sudoblock.

**`=< v0.6.0`**

```yaml
greeter(target str = 'world')<-:
  ->: print Hello {{target}}
```

**`Future`**

```yaml
def greeter(target str = 'world'):
  =: print Hello {{target}}
```

When the syntax is stable, this project will be formally released. Please reach out via [discord](https://discord.gg/7uVUfUVD7K) if you want to talk directly about it in the meantime. 

### Code of Conduct

Everyone interacting in the tackle project's codebases, issue trackers, chat rooms, and mailing lists is expected to follow the [PyPA Code of Conduct](https://github.com/pypa/.github/blob/main/CODE_OF_CONDUCT.md).

## Credit

Special thanks to [audreyfeldroy](https://github.com/audreyfeldroy) for creating [cookiecutter](https://github.com/cookiecutter/cookiecutter), the basis for this project. Would not have been possible without it and other core dependencies like [pydantic](https://github.com/pydantic/pydantic) and [jinja](https://github.com/pallets/jinja).
