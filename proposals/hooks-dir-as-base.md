---
id: hooks-dir-as-base
title: Hooks Dir as Base
status: implemented
description: Allow the base of a provider be either a hooks dir or tackle file
issue_num: 240
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Hooks Dir as Base

Allow the base of a provider be either a hooks dir or tackle file

- Proposal Status: [implemented](README.md#status)
- Issue Number: [240](https://github.com/sudoblockio/tackle/issue/240)
- Proposal Doc: [hooks-dir-as-base.md](https://github.com/sudoblockio/tackle/blob/main/proposals/hooks-dir-as-base.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

When there is no tackle file in a directory, it would be appropriate to instead check if there is a hooks dir as well since if there was a tackle file, then those hooks in the hooks dir would also be parsed.

> Relates to [current-directory](path-tracking.md)

## Implementation

- [ ] Change the finding procedure

```python
CONTEXT_FILES = {
    '.tackle.yaml',
    '.tackle.yml',
    '.tackle.json',
    'tackle.yaml',
    'tackle.yml',
    'tackle.json',
}


def find_tackle_file(provider_dir) -> str:
    """Find the tackle files based on some defaults and return the path."""
    provider_contents = os.listdir(provider_dir)
    for i in provider_contents:
        if i in CONTEXT_FILES:
            return os.path.join(provider_dir, i)

    raise InvalidConfiguration(f"Can't find tackle file in {provider_dir}")
```

This should instead return a tuple with the tackle file and the hooks dir.

Use 1:

```python
def import_local_provider_source(context: 'Context', provider_dir: str):
    """
    Import a provider from a path by checking if the provider has a tackle file and
    returning a path.
    """
    context.input_dir = provider_dir
    if context.input_file is None:
        context.input_file = find_tackle_file(provider_dir)

    if context.directory:
        context.input_file = os.path.join(context.input_file, context.directory)

    extract_base_file(context)
```

Use 2

```python
    elif is_directory_with_tackle(first_arg):
        # Special case where the input is a path to a directory. Need to override some
        # settings that would normally get populated by zip / repo refs. Does not need
        # a file reference as otherwise would be given absolute path to tackle file.
        context.input_file = os.path.basename(find_tackle_file(first_arg))
        context.input_dir = Path(first_arg).absolute()
```

Done? No. Will need to check:

- [ ] Does it call the default hook on no arg?
- [ ] Does an error return when there is no arg / default hook in hooks dir?
- [ ] Does help work right?

Most likely also need to update extract_base_file(context: 'Context')

```python
def extract_base_file(context: 'Context'):
    """Read the tackle file and initialize input_context."""
    if context.find_in_parent:
        try:
            path = find_in_parent(context.input_dir, [context.input_file])
        except NotADirectoryError:
            ...
```

- What is `context.input_file`?

```python
def find_in_parent(dir: str, targets: list, fallback=None) -> str:
    """Recursively search in parent directories for a path to a target file."""
    for i in os.listdir(dir):
        if i in targets:
            return os.path.abspath(os.path.join(dir, i))
# Errors...
```