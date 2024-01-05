---
id:
title: Return Key
status: wip
description: Create a special key for returning the value when parsing
issue_num: 245
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Return Key

Create a special key for returning the value when parsing

- Proposal Status: [wip](README.md#status)
- Issue Number: [245](https://github.com/sudoblockio/tackle/issue/245)
- Proposal Doc: [return-key.md](https://github.com/sudoblockio/tackle/blob/main/proposals/return-key.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

> Blocked by [return-hook](return-hook.md)

Currently when a declarative hook is called with an exec, the entire context is parsed with a special field for returning the appropriate value (`return`) being used to specify what the result is of that parsing.

This proposal would modify the parsing behaviour so that special keys can be used to indicate whether a variable  is returned.

## Examples

Normal parsing
```yaml
foo: bar
return->: return {{foo}}
```


## Macros

```yaml
foo: bar
return->: return {{foo}}
```

Then move to using return hook.
```yaml
foo: bar
tmp:
  ->: return {{foo}}
```
