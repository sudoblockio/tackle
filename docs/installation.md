# Installation

Tackle-box aims to be cross-platform (linux, windows, mac) and can be installed via python's package manager, pip.

```shell
pip install tackle-box
```

Tackle-box has the capability to install additional package dependencies from hooks. If you wish to keep your system python interpreter clean of packages, you should use a virtual environment.

```shell
python3 -m venv env
source env/bin/activate
pip install tackle-box
```

Alternatively, to build from source:

```shell
git clone https://github.com/robcxyz/tackle-box
cd tackle-box
python3 -m venv env
source env/bin/activate
python setup.py install
```