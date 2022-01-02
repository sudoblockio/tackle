# Tackle Box

[![pypi](https://img.shields.io/pypi/v/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![python](https://img.shields.io/pypi/pyversions/tackle-box.svg)](https://pypi.python.org/pypi/tackle-box)
[![codecov](https://codecov.io/gh/robcxyz/tackle-box/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/github/robcxyz/tackle-box?branch=main)
[![main-tests](https://github.com/robcxyz/tackle-box/actions/workflows/main.yml/badge.svg)](https://github.com/robcxyz/tackle-box/actions)

* Tackle Box Documentation: [https://robcxyz.github.io/tackle-box](https://robcxyz.github.io/tackle-box)-> WIP
* GitHub: [https://github.com/robcxyz/tackle-box](https://github.com/robcxyz/tackle-box)
* PyPI: [https://pypi.org/project/tackle-box/](https://pypi.org/project/tackle-box/)
* Free and open source software: [BSD license](LICENSE)

Tackle box is a declarative DSL for building modular workflows and code generators. Tool is plugins based and can easily be extended by writing additional hooks or importing external providers creating a web of interoperable CLIs.

> WARNING - Project still alpha. Will be officially released shortly.

### Demo

```
pip3 install tackle-box

# General tour of tackle box
tackle robcxyz/tackle-demos

# Create a new provider in one minute
tackle robcxyz/tackle-provider

# Push to github and now you can call it
tackle <your GH username>/tackle-your-provider
# Or alternatively import/call it from another tackle file
```

[comment]: <> (### Use Cases)

[comment]: <> (Tackle box has a wide variety of use cases. Here are a few for inspiration.)

[comment]: <> (- [Code generation]&#40;&#41; - WIP)

[comment]: <> (- [Custom workflows]&#40;&#41; - WIP)

[comment]: <> (- [Keeping configuration files dry]&#40;&#41; - WIP)

[comment]: <> (- [Kubernetes]&#40;&#41; - WIP)

### Features

- Declarative: Everything is in yaml with easy to use interfaces
- Turing complete: Loops, conditionals and branching is supported
- Extensible: New providers can be created or imported remotely
- Lean: Tackle box has only 4 dependencies - core logic <1k LOC

### Basic Usage / Structure

Tackle-box can be called against any yaml/json file or remote location by specifying the path to a repo / directory. By default, tackle looks for a `tackle.yaml` file in the target location which is parsed sequentially with each key traversed looking for hook calls indicated by an arrow (`->`). Tackle box ships with ~70 hooks to do basic prompting / code generation / system operations but can easily be extended by writing additional hooks.

For instance given the following directory structure:

```
├── hooks
│ └── stuff.py
└── tackle.yaml
```

With `stuff.py` looking like:

```python
class Stuff(BaseHook):
    type: str = "do-stuff"
    things: str
    _args: list = ['things']

    def execute(self):
        print(self.things)
        return self.things
```

One could run a tackle file that looks like this:

```yaml
a-key->: do-stuff do-things
b-key:
  if: a-key == 'do-things'
  ->: do-stuff
  things: All the things
```

Which when run would print out "All the things" twice and result in the following context:

```yaml
compact: All the things
expanded: All the things
```

Which you can use to then generate code, print out to file, or do any number of custom actions with additional hook calls.

### Road Map

The main challenge with this project is going to be reaching a stable syntax that people can reliably build on. Until that happens any feedback is welcome that could help make any of the interfaces, both in the core parsing logic / hook interfaces, is welcome. A place outside of github issues will be made to better accommodate those conversations.

### Code of Conduct

Everyone interacting in the Cookiecutter project's codebases, issue trackers,
chat rooms, and mailing lists is expected to follow the
[PyPA Code of Conduct](https://www.pypa.io/en/latest/code-of-conduct/).

## Credit

Special thanks to the [cookiecutter](https://github.com/cookiecutter/cookiecutter) community for creating the inspiration for this project.

