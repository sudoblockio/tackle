---
id:
title: Splat Syntax
status: wip
description: Allow for using splat syntax similar to how jinja uses it but in normal hook calls
issue_num: 259
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

[//]: # (--end-header--start-body--MODIFY)

# Special Args

Would be convenient to be able to call tackle with a couple reserved arguments for doing actions that should be integrated directly into tackle. For instance:

`tackle freeze [provider_name]`

`tackle import [provider_name]`

`tackle update [provider_name]`

Would be available


### Special Things

- Special variables
- Special args
- Special keys
- Special fields
- Special methods


#### Special Methods

```yaml
F<-:
  ...

f->: F json_str
```

- json
- json_str
- yaml
- yaml_str
- json_schema
- validate
