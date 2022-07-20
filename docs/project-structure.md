# Project Structure

Tackle box parses arbitrary configuration files (yaml / toml / json) called `tackle files` and only modifies the content with the calling of a `hook`. Hooks can be both written in python or declared within the tackle files and are grouped into `providers`. Providers don't necessarily need to have hooks or tackle files but logically would have at least one of them to do anything. So to be explicit:

- `tackle file`
  - A configuration file that runs or declares hooks
  - By default it is a file called `tackle.yaml` and is located at the base of a provider
  - Can be called by other tackle files or can be imported to gain access to hooks declared within the tackle file
  - Additional docs can be found [here](writing-tackle-files.md) for how to write tackle files
- `hook`
  - A reusable piece of logic that can be called from within tackle files
  - Either [written in python](python-hooks.md) or [declared within a tackle file](declarative-hooks.md)
  - Both python and declarative hooks are strongly typed and contain attributes to make calling them easy
- `provider`
  - An importable / callable collection of hooks and / or a tackle files that runs hooks
  - Tackle ships with a core set of native providers to do basic prompting / system operations / code generation
  - Third party providers are generally stored in github repos and can be imported / called from other tackle files
  - Additional docs can be found [here]() for how to create providers

For instance this is the basic layout of a provider:

```
├── hooks
│ └── hook-1.py
│ └── hook-2.py
│ └── requirements.txt
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

## Remote providers

Tackle adheres to the [XDG base directory specification](https://wiki.debian.org/XDGBaseDirectorySpecification#:~:text=The%20XDG%20Base%20Directory%20Specification,configuration%2C%20data%20and%20runtime%20files.) and stores all the local configuration files in `~/.config/tackle` such as providers which are stores at `~/.config/tackle/providers/<provider org>/<provider name>`.

[//]: # (A local settings file can be stored at `~/.config/tackle/settings.yaml` )


