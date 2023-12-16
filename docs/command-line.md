# Calling from the Command Line

Tackle is extremely flexible on the inputs that it accepts to run against. Basically any file, directory, or repo are acceptable inputs or no input at all. This document describes the logic behind how tackle takes in inputs including how additional args, kwargs, and flags are interpreted from the command line.  

For how to structure files for a tackle provider, check out [creating providers](./creating-providers.md) or creating self documenting CLIs check out [declarative cli](./declarative-cli.md).

> Note: Calling tackle from the command line or from within a tackle file with a [tackle hook](providers/tackle/tackle.md) is basically the same with the context being passed along calls.

## Targets

Targets are the first argument in any tackle call. For instance:

```shell
tackle TARGET arg1 arg2 --key value --flag
```

The below describes the logic around how to qualify a target.

### File Targets 

Tackle can be called against any yaml file or json. Tackle runs the file as if it is in the current directory.

```shell
tackle some/file/location.yaml
```

You can also use the file flag.

```shell
tackle --file some/file/location.yaml
```

### Directory

Tackle can be called against any directory and looks for a "tackle file", a file that matches `tackle.yaml/toml/json` or `.tackle.yaml/toml/json` and runs against that.

```shell
tackle some/directory/location
```

You can use the key word argument `directory` or `d` for short.

```shell
tackle --directory some/directory/location
```

### Repository

Tackle can be called against any repository looking input which similar to a directory input, looks for a "tackle file" and runs against that.

Repository sources can be abbreviated such that the following items are equivalent.

- [https://github.com/robcxyz/tackle-provider](https://github.com/robcxyz/tackle-provider)
- [github.com/robcxyz/tackle-provider](https://github.com/robcxyz/tackle-provider)
- [robcxyz/tackle-provider](https://github.com/robcxyz/tackle-provider)

```shell
tackle robcxyz/tackle-provider
```

You can also specify files / directories 

```shell
tackle robcxyz/tackle-provider --d some/directory/location -f some-file.yaml
```

### Zipfile

Tackle can also run against a zip file.

```shell
tackle path/to/some/zipfile.zip
```

### Unknown Target / No Target 

When a target is not recognized as a file, directory, repo, or zipfile, tackle attempts to use the target as an argument to the nearest tackle provider which is any directory with a tackle file or hooks directory. Nearest in this context means in the current directory, the parent directory, and so forth until no tackle provider is found. 

Call the nearest tackle provider (in this case in the parent directory) with target as argument.

```shell
# └── .tackle.yaml/json file or .hooks directory
#    └── calling directory
tackle unknown-target
```

Or simply call `tackle` without a target which will do same as above. 

```shell
tackle
```

## Additional Args / Keyword Args / Flags

When calling a target, additional args / kwargs / flags can be supplied via the command line or through calling a [tackle hook]() from within a tackle file.  

### Argument matches tackle file's key

When an input is supplied but it does not match any of the above criteria, by default tackle checks if there is a key in the parent directory and runs from that key. Logic is described in the next section.

```shell
tackle a-tackle-file.yaml a-key  # a-key is a key in the tackle file
```

## Additional Arguments / Keys / Flags

The preceding section described how targets are handled but tackle can also take in arbitrary args, key value pairs, and flags which are interpreted.  

```shell
tackle target ARGs --KEYs VALUEs --FLAGs
```

### Extra Arguments

Additional arguments are interpeted as the user doesn't want to run an entire tackle file but run a specific set of keys. So for instance given the following tackle file:

File:
```yaml
key_a->: print Key A
key_b->: print Key B
```

Command:
```shell
tackle file.yaml key_a
```

Only `key_a` would be run.

This is useful if you want to only run a subsection of a tackle file or jump straight to a command.

### Extra Key Values and Flags

Additional key value pairs and flags are interpreted by command line calls as being overrides to the context. For instance given the following tackle file and call:

File:
```yaml
key_a->: input What to set `key_a`?
key_b->: print "{{key_a}}"
```

Command:
```shell
tackle file.yaml --key_a "stuff and things"
```

Would result in no prompt and "stuff and things" printed to the user.

Flags are the same as key value pairs but override with True.

## Additional Command Line Arguments

### override / -o

To override some inputs in the tackle file or to insert extra values, use the `override` option to point to a file with those extra values.  For instance:

```shell
tackle path/to/something --override some-file.yaml
```

Calling from python allows for assignment of variables via dicts or kwargs. See the [testing providers docs](testing-providers.md) for more information on calling tackler from python.

### --print / -p

When the print flag is specified, the context after parsing is printed out to the screen which can then be piped to a file.

```shell
tackle --print TARGET
```

### --print-format [json/yaml/toml] / -pf [json/yaml/toml]

Regardless of if the print flag is selected, print the output in the arguments format.

Must be one of json, yaml, or toml. Defaults to json.

```shell
tackle --pf yaml
```
