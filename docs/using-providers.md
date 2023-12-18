# Using Providers

Providers can be called directly from the command line per the [calling tackle](command-line.md) documentation or within a tackle file with the two ways essentially mirroring one another.

For instance from the command line:
```shell
# Remote providers
tackle sudoblockio/tackle-provider  # Defaults to github org/repo
tackle https://github.com/sudoblockio/tackle-provider
# Local providers
tackle path/to/dir/with/tackle/file
tackle path/to/tackle/file.yaml
tackle  # See notes below
```

Or from within a tackle file using the [tackle hook](providers/tackle/tackle.md):
```yaml
call local tackle->: tackle path/to/local/provider
call remote tackle->: tackle sudoblockio/tackle-provider
```

Both versions can take args, kwargs, or flags if the tackle provider supports consuming them, otherwise an error will be raised unless these values have been consumed by the end of execution.

From command line:
```shell
tackle some/provider some_arg --some kwarg --some_flag
```

From tackle file:
```yaml
call tackle->: tackle some-source some_arg --some kwarg --some_flag
```

## Remote Providers

Tackle ships with numerous native providers but additional ones can be accessed when they are committed to a git repository like on github. Remote providers can be

By default, tackle uses the **latest versioned release** of a provider but to use the latest commit, one can add the `--latest` flag to override this default and use the latest commit from the default branch. Additionally, a specific release can be used by specifying the `--checkout` flag.  

- `tackle gh-org/repo`
    - If there is a release, use that
    - Otherwise use latest commit
- `tackle gh-org/repo --latest`
    - Use the latest commit regardless of release
- `tackle gh-org/repo --checkout v0.1.0`
    - Use a specific release


### Calling Tackle with File / Directory Args

When remote providers are used, directories and files can

```text
├── hooks
│ └── hooks.py # Defines a hook
└── a-dir
  └── a-file.yaml # Uses the hook
```

```shell
tackle gh-org/gh-repo --file a-dir/a-file.yaml
```

Alternatively you could specify a directory as in this case:

```text
├── hooks
│ └── hooks.py
└── a-dir
  └── tackle.yaml
```

```shell
tackle gh-org/gh-repo --directory a-dir
```

### Calling Tackle with No Args / Unknown Args

When calling `tackle` without any arguments or arguments that do not point to a tackle provider, tackle then looks for tackle providers in the parent directories. A tackle provider is any directory that has one of the following:

- A tackle file
  - `tackle.yaml`
  - `.tackle.yaml`
  - `tackle.json`
  - `.tackle.json`
  - `tackle.toml`
  - `.tackle.toml`
- A hooks directory
  - `hooks`
  - `.hooks`

Similarly, if tackle is called with an argument that does not look like a remote repo (ie `str/str` - two strings separated by a slash), it will then look in the parent directory for a tackle base and use that arg for that execution.

> The reasoning for supporting this logic is one of the nice use cases of tackle in having a set of commands you might want to run regardless of where you are in a directory tree. A couple use cases could be:
>
> 1. A repo with a common set of commands that you want to run in a subdirectory. For instance lets say you have a bunch of IaC/k8s manifests and you want to run them with `tackle apply file.yaml`. the logic for apply could be in the parent and be available anywhere in the repo.
>
> 2. Common commands in the home directory. For instance you could have a tackle file with a hook `ssh` and run `tackle ssh` anywhere in your system and it would run that hook.
>
> There are more use cases but regardless, tackle is trying to be intelligent about what the arguments you give it means and if the arg is not recognized as a source, then it should do its best to try to resolve what that command means.


### Importing hooks from a provider

Hooks can be imported from a tackle provider with the [import](providers/Tackle/import.md) hook but only hooks defined in a `hooks` directory. Hooks defined in the root tackle file (ie `some-provider/tackle.yaml`) can not be imported. To import hooks you can use the following syntax within tackle file, both in the root or in documents within the hooks directory (ie `some-provider/hooks/a-file.yaml`).

```yaml
# Using a special key as str
import_>: path/to/local/or/remote/provider --latest
# Or
import_>:
  - path/to/provider1
  - path/to/provider2 --version v1.0
  - path/to/provider3 --latest
# Or
import_>:
  - src: remote/provider
    version: v1.0
  - src: path/to/provider
    latest: true
# Calling `import` hook
do some import->: import path/to/local/or/remote/provider

# Finally - using the imported hook
using that hook->: the_imorted_hook ...
```

Here we use a [private hook call](writing-tackle-files.md#public-vs-private-hook-calls) to import hooks as the output of this hook call is not needed.

