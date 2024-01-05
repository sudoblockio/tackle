---
id:
title: Pydantic 2.0 Upgrade
status: implemented
description: Upgrade to pydantic version 2.0
issue_num: 253
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Pydantic 2.0 Upgrade

Upgrade to pydantic version 2.0

- Proposal Status: [implemented](README.md#status)
- Issue Number: [253](https://github.com/sudoblockio/tackle/issue/253)
- Proposal Doc: [pydantic-2-upgrade.md](https://github.com/sudoblockio/tackle/blob/main/proposals/pydantic-2-upgrade.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

- Custom Field
  - Need to create new Field object poc
  - Added fields
    - arg_num
    - render_by_default
    - visible
    - hidden
  - Could also strongly type the field which would be very helpful.
    - This should not work but it does. Should have error as the `bar: baz` is discarded

- New Config


- Replace `__fields__`
  - model_config

```yaml
Schema<-:
  foo:
    type: str
    default: bar
    bar: baz

success->: Schema
```


- `create_model`
  - ok

- ModelMetaclass
- ConfigError
- smart_union
  - TypeError: GenerateHook.__init_subclass__() takes no keyword arguments
-