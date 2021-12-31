# Calling Tackle-box

Tackle-box is extremely flexible on the inputs that it accepts to run against. Basically any file, directory, or repo are acceptable inputs or no input at all. This document describes the logic behind how tackle takes in inputs including how additional args, kwargs, and flags are interpreted from the command line.  

## Targets

Targets are the first argument in any tackle call. For instance:

```shell
tackle TARGET arg1 arg2 --key value --flag
```

### File

Tackle can be called against any yaml file or json. Tackle runs the file as if it is in the current directory.

```shell
tackle some/file/location.yaml
```

### Directory

Tackle can be called against any directory and looks for a "tackle file", a file that matches `tackle.yaml/yml/json` or `.tackle.yaml/yml/json` and runs against that.

```shell
tackle some/directory/location
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

### Zipfile

Tackle can also run against a zip file.

```shell
tackle path/to/some/zipfile.zip
```

### No argument supplied

When no input argument is supplied, tackle by default looks in the parent directories for the nearest tackle file and runs that. This is useful if you want to store a collection of calls that

```shell
tackle
```

### Argument matches parent tackle file's key

When an input is supplied but it does not match any of the above criteria, by default tackle checks if there is a key in the parent directory and runs from that key. This is logic on the next section's logic.

```shell
tackle a-key  # In the parent tackle file
```

## Additional Arguments / Keys / Flags

Preceeding section described how targets are handled but tackle can also take in arbitrary args, key value pairs, and flags which are interpreted.  

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

