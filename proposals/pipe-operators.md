---
id:
title: Filters / Pipe Operators
status: wip
description: Allow for jinja / bash style filters / pipes
issue_num: 249
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Filters / Pipe Operators

Allow for jinja / bash style filters / pipes

- Proposal Status: [wip](README.md#status)
- Issue Number: [249](https://github.com/sudoblockio/tackle/issue/249)
- Proposal Doc: [pipe-operators.md](https://github.com/sudoblockio/tackle/blob/main/proposals/pipe-operators.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

```yaml
Hook1<-:
  foo: str
  bar: str  
  args: [foo]

call->: literal baz | Hook1 --bar bazz
```