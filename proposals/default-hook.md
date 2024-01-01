---
id: default-hook
title: Default Hook
status: implemented
description: Allow files to have a default hook to be called when no arguments are supplied
issue_num: 232
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Default Hook

Allow files to have a default hook to be called

- Proposal Status: [implemented](README.md#status)
- Issue Number: [232](https://github.com/sudoblockio/tackle/issue/232)
---
[//]: # (--end-header--start-body--MODIFY)

# Default Hook

> Status: Implemented

Currently, there is no way to call a tackle file without an argument and have any kind of exposed schema which would lend itself to building a defined schema that could be rendered into a help screen. This proposal aims at defining that default interface so that

### Questions

- What happens to parsing the regular context?
  - It should throw error if default hook does not have field
    - Thus, it should be parsed first
  - If the outer context is not parsed, then it is unreachable
    - The outer context should be executed after the default hook

- What happens to a file that is called via a tackle hook with a default hook?
  - If there is no arg, then normally with the default hook
  - Default hook does not get exported as it is only local to the file

- What is the meaning of a private default hook?
  - There is no such thing as a private default hook
    - Default hooks are by default the exposed interface of a file, can't be private
  - The only natural meaning of having an arrow change (ie `<_`/`<-`) is informing something about order
    - `<-` - Before outer context
    - `<_` - After outer context
  - Do not implement this

### Examples

```yaml
<-:
  str_input: str
  list_input:
    type: list
    default: []
```

+ Simple
+ No other meaning

```yaml
init<-:
  str_input: str
  list_input:
    type: list
    default: []
```

- Need to know semantics
- Wipes out use of init or other as function
- This is irrelevant

### Public vs Private -> Before / After

```yaml
<-:
  str_input: str
  list_input:
    type: list
    default: []

do->: tackle {{str_input}}
```

```yaml
do->: tackle {{str_input}}
<-:
  ...
```

- Biggest use case of post default hooks is importing other hooks and having them be part of the help menu
  - This is because in the prior case, the hook is run first and then made available to the context
  - When this happens, the schema is validated and if there is an error, it will not want to parse the outer context by default, it will just error which in this case falls back to the help menu.  
  - When we have this help menu and the outer context has not been parsed, then no imported options are available
  - `Issue is we don't know if that is all we are supposed to do`
  - This should be accomplished by running the hooks dir
- No other use case makes sense

```yaml
<_:
  str_input: str
  exec: ...
do->: import foo
---
# WRONG
<_:
  str_input: str
#   No exec / no action
do->: tackle {{str_input}}
---
# WRONG  
<_:
  str_input: str
#   No exec / no action
do->: print foo
```

#### Empty File Actions

- If there is a default hook, run that
  - If the hook has no exec, doesn't matter as that logic is downstream
    - But this should
  - If you want to have the default being displaying the help, this should be hacked in?
    - Would block outer context
- If there is a default hook and context, then run default then it will run context.

- **Issue is that it should be clear what is wrong when params are needed**
  - Something needs to be defaulting to help -> at least when the CLI fails

## Implementation

- [x] First pass on functions, RM special key
- [x] If key exists, parse it with global args / kwargs
- [x] Then parse normally
  - Need to mod part where it takes global_args and tries to parse from keys
    - ?? -> No?
