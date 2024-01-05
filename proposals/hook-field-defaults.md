---
id: hook-field-defaults
title: Hook Field Defaults
status: implemented
description: Allow flexible ways to declare hook field defaults
issue_num: 237
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Hook Field Defaults

Allow flexible ways to declare hook field defaults

- Proposal Status: [implemented](README.md#status)
- Issue Number: [237](https://github.com/sudoblockio/tackle/issue/237)
- Proposal Doc: [hook-field-defaults.md](https://github.com/sudoblockio/tackle/blob/main/proposals/hook-field-defaults.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

Declarative hook default values should be parsed for hook calls.


```yaml
<-:
  literal: val
  literal_compact->: input
  literal_expanded:
    ->: input
  field:
    type: str
    default: foo
  field_default_compact:
    type: str
    default->: input  
  field_default_expanded:
    type: str
    default:
      ->: input
```

Ways to implement

1. Macro + type handler  
  - Rewrites the input in expanded form
  - When 'default' key is a dict, create a special dict type that can be parsed later in the absense of a supplied input.
    - Can't parse right away as we don't know if this is a user supplied variable
    - Don't know the type either so it either needs to be supplied (normally with `default` key, you don't need to give `type`) or it is set as Any until the `default` dict is parsed.
    - Needs to be done when we compile the hook

```yaml
<-:
  # from
  literal_compact->: input
  # to
  literal_compact:
    default:
      ->: input
  # from
  literal_expanded:
    ->: input
  # to
  literal_expand:
    default:
      ->: input
  # This is an issue because the default has no type
  # from
  field_default_compact:
    type: str
    default->: input  
  # to
  field_default_compact2:
    type: str
    default:  
      ->: input
```

Calling tackle externally

- Before we had an extra context being passed into the `tackle` hook call which made sense as we didn't have specific variables to populate a hook's strongly typed interface.


## Issues

1. For the prompt hooks, the msg without the `message` field is the key which in this case the `default`, not what we want
> This is probably not an issue as the `default` is just the key that refs the value. Not the key that is actually in the dict
  - Options
    - We can catch the issue in the hook itself
      - Wouldn't take much work to check if the key is `default` and then look the parent key but then all keys called `default` would have the erroneous behaviour
    - When we interpret the special dict, we can run another macro to rewrite the value back to the original key
      - Could write directly to the proper context
        - ??? What context?