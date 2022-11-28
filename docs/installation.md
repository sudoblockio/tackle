# Installation

Tackle aims to be cross-platform (linux, windows, mac) and can be installed via python's package manager, pip.

> Warning -> tackle can install additional packages. Keep reading document for recommended installation settings.

### Simplest installation
```shell
pip install tackle
```

> Windows users: Tackle strives to be fully functional on windows but has some [incompatibilities](https://github.com/robcxyz/tackle/actions/workflows/main-windows.yml).  Accepting PRs.

### Intermediate installation

Tackle has the capability to install additional package dependencies from hooks. If you wish to keep your system python interpreter clean of packages, you should use a virtual environment.

```shell
python3 -m venv env
source env/bin/activate
pip install tackle
```

### Best installation method

An even better way of using tackle is creating a function that by default activates a virtual environment, runs a tackle command, and deactivates the environment when done. For that, create a virtual environment (steps from above), install tackle, and then put this function changing the path to your virtual environment in your `~/.zshrc` / `~/.bashrc`.

```shell
tackle() {
    # Change this path to your virtual environment!
    source ~/code/tackle/env/bin/activate  
    # And this one!
    ~/code/tackle/env/bin/tackle "$@"  
    deactivate
}
```

> Note: PRs welcome for windows for above method

### Installing additional dependencies

As mentioned, tackle has an import system that is able to install additional pip dependencies but you can also install dependencies for local hooks when you install tackle initially. To do that, run:

```shell
pip install "tackle[all]"
```

Note, if you import another provider, it may still have additional dependencies.

### Building from source

If you want to contribute / build from source, run the following.

```shell
git clone https://github.com/robcxyz/tackle
cd tackle
python3 -m venv env
source env/bin/activate
python setup.py install
```