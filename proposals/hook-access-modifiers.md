---
id: hook-access-modifiers
title: Hook Access Modifiers
status: implemented
description: Make hooks either public or private allowing distinction for what is in `tackle <target> help`.
issue_num: 235
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Hook Access Modifiers

Make hooks either public or private allowing distinction for what is in `tackle <target> help`.

- Proposal Status: [implemented](README.md#status)
- Issue Number: [235](https://github.com/sudoblockio/tackle/issue/235)
- Proposal Doc: [hook-access-modifiers.md](https://github.com/sudoblockio/tackle/blob/main/proposals/hook-access-modifiers.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

Hooks right now are all in the same namespace but if they are to be used as interfaces / rendered into help, they need to be namespaced in a way that allows collections of hooks to be exposed and others to remain hidden. The natural way to do this would be in allowing hooks with different signs to play a role in different

- Python hooks are private by default
- Declarative hooks are implicitly either private / public through arrow sign
- Private hooks are still exported across files \
- Public hooks can be called externally and are rendered into help screen

### Examples

```yaml
private_hook<_:
  stuff: things
public_hook<-:
  stuff: things
```

Help screen with default hook -> `tackle --help`:

```text
Help: default help  

Args:
  public_hook - help...
  default_hook_method - help...

Flags:
  default_hook_arg - (str) - help...
```

```yaml
<-:
  help: A thing that does stuff

  default_hook_arg: str

  default_method<-:
    param: str

base-method<-:
  param: Foo
```

- Params are function specific

```yaml
base<_:
  base-param: str

<-:
  extends: base
  help: A thing that does stuff

  default_hook_arg: str

  default_method<-:
    param: str

base-method<-:
  extends: base
  param: Foo
```


## Implementation

- [x] Divide `provider_hooks` into `public_hooks` and `private_hooks`
- [x] Implement default hooks as they should be in place before since there will be logic around them
- [x] Lookups need to then be updated
  - ? -> wtf is this?
- [x] Implement help screen

