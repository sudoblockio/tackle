---
id:
title: Splat Operators
status: implemented
description: Allow splat operators to instantiate hooks - ie `a_hook **a_dict` or `a_hook *a_list`
issue_num: 257
blockers:
- ast-parser
- peg-parser
---
[//]: # (--start-header--DO NOT MODIFY)

# Splat Operators

Allow splat operators to instantiate hooks - ie `a_hook **a_dict` or `a_hook *a_list`

- Proposal Status: [implemented](README.md#status)
- Issue Number: [257](https://github.com/sudoblockio/tackle/issue/257)
- Proposal Doc: [splat-operators.md](https://github.com/sudoblockio/tackle/blob/main/proposals/splat-operators.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

> Could be done with the [peg parser proposal](./peg-parser.md)

Would be really helpful to support splat syntax like this.

```yaml
obj<-:
  foo: bar

data:
  foo: baz

call_with_tpl->: obj **{{data}}
call_no_tpl->: obj **data
call_raw->: obj **{'foo':'bar}
```

With splat, you don't need templating as it is always going to be a reference to a var.

This is most helpful when the `data` is in another file. For my use case, I want to have a number of files that all have the same schema. In that case, I want to be able to quickly validate if the data is right and not have to run full business logic to see if it is right.

### Implementation

- tokenize the splat operators
- run macro on output before parsing
