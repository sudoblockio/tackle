---
id: hook-methods
title: Hook Methods
status: wip
description: Allow creating hooks within hooks that act like methods with parameter inheritance.
issue_num: 239
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Hook Methods

Hooks should have methods that can be called against the hook

- Proposal Status: [wip](README.md#status)
- Issue Number: [239](https://github.com/sudoblockio/tackle/issue/239)
---
[//]: # (--end-header--start-body--MODIFY)

# Hook Methods

> Status: Implemented

Right now the order of operations for how to run and access a hook method is all messed up and needs to be rebuilt. Current there are two places where methods can be called, 1, within a tackle file and 2, from command line. Ideally they should be converged.

## Old Implmentation

### Within tackle file

- In this case, `tackle` needs to be explicitly called to allow for calling a default hook

#### Flow

- Splits up hooks with `.` in them, ie `hook_name.hook_method`
- Finds top level hook
- Iterates through hook parts
  - Compile hook if LazyBaseFunction
  - Compile method
  - Inherit base fields

### As arg / kwarg / flag parser

- `tackle` is not explicitly called but is assumed with tackle file found in `extract_base_file`
- Hook can be default hook in tackle file
- Last arg can be `help` which runs that logic
  - `help` arg virtually never called within tackle file

#### Flow

- First detects that the input arg is a hook then passes that down to `find_run_hook_method`
  - Called from `run_source` which normalizes args / kwargs / flags
- Loops through arguments
  - If arg is in hook fields and type is callable
    - Compile with inherit
  - If LazyBaseFunction
    - Compile and inherit
  - If help
    - `run_help`
  - If hook has args, use that in hook

### Issues

- Repeated logic
  - Same thing that happens in CLI should be happening within the tackle file
  - This is super nitty gritty and should perfect the logic in one place
- Calling from tackle file different as depends on `.` separator
  - Not intuitive -> Should mirror

## Current Functions

- get_hook(hook_name: str, context: 'Context') -> Type[BaseHook]
  - Returns executable
  - Normally `unpack_args_kwargs_string` is called before which processes args/kwargs/flags
  - For CLI run, this is not possible unless we assert the first arg is a hook \
  - If we do this, then we can pass the unconsumed args and kwargs/flags into whatever logic we need
- find_run_hook_method(context: 'Context', hook: ModelMetaclass, args: list, kwargs: dict) -> Any
  - Takes hooks and calls it
- run_source(context: 'Context', args: list, kwargs: dict, flags: list) -> Optional:
  - Process global args/kwargs/flags


## New Implementation


- `get_hook` -> `get_public_or_private_hook`
  - get_hook()
  - Only takes one arg
  - Returns base of the hook
- `enrich_hook`
  - enrich_hook(context: 'Context', Hook: ModelMetaclass, args: list, kwargs: dict) -> Hook
  - Uses unconsumed args and kwargs + flags as kwargs
    - If arg = help and is last arg, `run_help`
    - Args first tried to be used as methods
      - Compile is necessary
    - Args then applied if args field exists, otherwise this is an error
    - Kwargs then applied to hook
- `run_hook`
  - Calls the hook -> Not needed?

### Flow

- Compile LazyBaseFunction
- Iterates through args
