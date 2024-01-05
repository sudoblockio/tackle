---
id: command-arrow
title: Command Arrow
status: wip
description: Add macro to easily call commands on different platforms
issue_num: 227
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Command Arrow

Add macro to easily call commands on different platforms

- Proposal Status: [wip](README.md#status)
- Issue Number: [227](https://github.com/sudoblockio/tackle/issue/227)
- Proposal Doc: [command-arrow.md](https://github.com/sudoblockio/tackle/blob/main/proposals/command-arrow.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

It is very common to want to run a system command which tackle should make simple. Issue is the parser and general mechanics are not very elegant right now. Solution should be clean to make it on par with being able to create a Makefile.

> See [command marker](./command-marker.md) for an alternative implementation

**Current**

```yaml
Single line->: command echo foo
Multiple lines:
  ->: command
  command: |
    echo foo1
    echo bar1
```

**Currently broken**

```yaml
Single line->: command echo --foo
```
Any args with a dash are parsed out

```yaml
Single line->: command "echo --foo"
```
This works though

```yaml
Multiple lines:
  ->: command
    echo foo1
    echo bar1
```

Also this
```yaml
Multiple lines->: command
  echo foo
  echo bar
```

But not this
```yaml
Multiple lines->: command
  echo --foo
  echo bar
```

## Approaches

#### Dollar Sign  

```yaml
call->: $echo foo bar
```

Would require changes to the hook running qualifying each key. Also doesn't easily extend to how this could be done in the context of declarative hooks which should have a simple way of handling.

Bad idea...

#### New Arrow

This is probably the cleanest approach

```yaml
public-declarative-hook<\: echo --foo bar
private-declarative-hook</: echo --foo bar
public-hook-call\>: echo --foo bar
private-hook-call/>: echo --foo bar
```

```yaml
public-declarative-hook:
  <\: echo --foo bar
  help: ...
private-declarative-hook:
  </: echo --foo bar
  help: ...
public-hook-call:
  \>: echo --foo bar
private-hook-call:
  />: echo --foo bar
public-declarative-hook-call->: public-declarative-hook
private-declarative-hook-call_>: private-declarative-hook
```

```yaml
multi line simple:
  <\: echo --foo bar
    a new command foo --bar
multi line inline<\: echo --foo bar
  a new command foo --bar
multi line symbol<\: |
  echo --foo bar
  a new command foo --bar
```

```yaml
multi line simple:
  option: str
  args: ['option']
  <\: echo --foo {{option}}
    a new command foo --bar
```

Best selling feature is the platform dependent call, something that we could implement in a hook but then that would be the only thing it would implement.


```yaml
os<\: echo --foo bar
os<\linux: echo --foo bar
os<\mac: echo --foo bar
os<\win: echo --foo bar
os<\bsd: echo --foo bar
```

```yaml
os<\:
  linux: echo --foo bar
  mac: echo --foo bar
  win: echo --foo bar
  bsd: echo --foo bar
  _: echo --foo barr
```

- This is probably the most interesting aspect of this as it makes the tool cross platform, something that things like Make struggle with  
- Should be able to override each other
  - Ie share same key (`os` in this example)

```yaml
call|cmd->: echo foo --bar  
call|cmd_>: echo foo --bar
call\>linux: echo foo --bar
```

Would also need some lookup tables for platform names and clear docs on how which platform name applies to which. For instance `linux` vs `ubuntu` should internally resolve where we first try `ubuntu` then try `linux`.

### Attributes

```yaml
os:
  help: Do os stuff
  <\: echo --foo default  
  <\linux: echo --foo bar
  <\mac: echo --foo bar
  <\win: echo --foo bar
  <\bsd: echo --foo bar
```


## Implementations

- macros
- ?

Alternative implementations would be too hacky most likely. Macros are an established pattern and can be hooked into the parsing logic easily.

### Macros

Macros would be run on dicts / function dict inputs and hence would expand keys based on

Input:

```yaml
os<\: echo --foo default
os<\linux: echo --foo bar
os<\mac: echo --foo bar
os<\win: echo --foo bar
os<\bsd: echo --foo bar
```

`tackle/macros/cmd_hook_flatten_macro`

```yaml
os<\:
  _: echo --foo default
  linux: echo --foo bar
  mac: echo --foo bar
  win: echo --foo bar
  bsd: echo --foo bar
```

`tackle/macros/cmd_hook_to_match_function_macro`

```yaml
os<-:
  return: do
  exec:
    do:
      ->: match
      case:
        linux/>: echo --foo bar
#          ...
        _: ...
```

> Note: This macro would then be used within the match hook so no need to run again within the tackle file import for dcl hooks

`tackle/macros/cmd_hook_to_command_hook_macro`

```yaml
os<-:
  return: do
  exec:
    do:
      ->: match
      case:
        linux:
          ->: command
          command: echo --foo bar
#          ...
        _: ...
```

> Note: If running macro against a declarative hook's dict (ie embedded), this would then be exposed as a method on the declarative hook.
