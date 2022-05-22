# Installation

Tackle-box aims to be cross-platform (linux, windows, mac) and can be installed via python's package manager, pip.

> Warning -> tackle can install additional packages. Keep reading document for recommended installation settings.

**Simplest installation**
```shell
pip install tackle-box
```

> Windows users: Tackle-box strives to be fully functional on windows but has some [incompatibilities](https://github.com/robcxyz/tackle-box/actions/workflows/main-windows.yml).  Accepting PRs.

Tackle-box has the capability to install additional package dependencies from hooks. If you wish to keep your system python interpreter clean of packages, you should use a virtual environment.

```shell
python3 -m venv env
source env/bin/activate
pip install tackle-box
```

> TODO: Document how to alias tackle in rc files.

Alternatively, to build from source:

```shell
git clone https://github.com/robcxyz/tackle-box
cd tackle-box
python3 -m venv env
source env/bin/activate
python setup.py install
```