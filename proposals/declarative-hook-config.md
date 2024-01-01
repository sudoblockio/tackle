---
id: declarative-hook-config
title: Declarative Hook Config
status: implemented
description: Allow hooks to have a model_config parameter exposing pydantic config params
issue_num: 231
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Declarative Hook Config

Allow hooks to have a model_config parameter exposing pydantic config params

- Proposal Status: [implemented](README.md#status)
- Issue Number: [231](https://github.com/sudoblockio/tackle/issue/231)
---
[//]: # (--end-header--start-body--MODIFY)

We should be able to customize the config on a declarative hook since it is possible with a python hook. For this though, we need to worry about order of operations as:  

1. The config is normally set on the base hook so we'll need to override that
2. The __config__ and __base__ fields are natively not allowed to be set together
    - Creating custom `create_model` function will allow this
3. Can't simply set the config via `SomeModel.model_config`

Solution seems to be #2 which will allow creation of the model with a custom config.


### Potential Forms

```yaml
S<-:
  foo: bar

  # 1
  __config__:
    extra: allow

  # 2
  Config:
    extra: allow

  # 3
  config:
    extra: allow

  # 4
  _config:
    extra: allow

  # 4
  config<-:
    extra: allow

  # 5
  Config<-:
    extra: allow
```

1. __config__
- Dunder methods are lame

2. Config
- Should be ok but sort of a little weird
  - Nothing else is capital (yet - see Alias)
  - Others could be
    - Validators / Validator
    - Export - List of fields to export - Could be done with `Return` if it was a list
    - Remove - List of fields to remove before exporting
  - Other fields that could be capitalized
    - Return
    - Exec -> No - then that would imply a rule for methods
    - Extends
- Capital field names should be based on convention methods in general
  - Capital fields names shouldn't have explicit meaning (looking at you Go)
- It would be very odd if the `Config` field clashed with someones schema
  - Perhaps `config`, but not `Config`
  - Either way, the input field `config` should be aliasable to `Config`
    - Perhaps we need an `Alias` key

> **RESOLUTION** - Use `Config` and create custom pydantic Config object which can be used to access any of the hook's config parameters

### New Hook Design

```python
from tackle import BaseHook, Field

def SomeHook(BaseHook):
    hook_name: str
    a_field: str = Field()  # Custom Field

    class Config:
        # Classic pydantic config params
        extra = 'allow'
        # Custom params
        args = ['a_field']
        is_public = True
```
- Little verbose
- Prevents any clashing of variable names that used to be an issue
- Emphasizes pydantic lineage and capabilities

```yaml
SomeHook<-:
  foo: str
  Config:
    extra: allow
    args: ['foo']
```

- Here, the `Config` key makes it a little more clear what items are configurable and

#### Alias


#### Implementation
