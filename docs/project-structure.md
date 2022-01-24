# Project Structure

Tackle box at its core is simply a way to call python objects from yaml files. These python objects are called `hooks` which are grouped into `providers` that can be imported / ran from within `tackle files`. Providers don't necessarily need to have hooks or tackle files but logically would have at least one of them to do anything. So to be explicit:

- `hook`
    - A python object that can be called from a yaml based tackle file.
    - Extends the `BaseHook` class and is located within a `hooks` directory of a provider
- `provider`
    - An importable / callable collection of hooks and / or a tackle file that runs hooks
    - Tackle ships with a core set of native providers to do basic prompting / system operations / code generation
    - Third party providers are generally stored in github repos
- `tackle file`
    - A yaml file that runs hooks
    - By default it is a file called `tackle.yaml` and is located at the base of a provider

For instance this is the basic layout of a provider:

```
├── hooks
│ └── hook-1.py
│ └── hook-2.py
└── tackle.yaml
```

Which if it was located in github could be called with `tackle <github org>/<repo name>`

For code generators and other utilities that don't have any custom hooks, the provider structure could be as simple as:

```
├── templates
│ └── file1.tpl
│ └── file2.tpl
└── tackle.yaml
```

Tackle files can also be run on their own or call one another.
