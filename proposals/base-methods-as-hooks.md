---
id: base-methods-as-hook
title: Base Methods as Hooks
status: wip
description: Allow base methods to be called directly as hooks
issue_num: 233
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Base Methods as Hooks

Allow base methods to be called directly as hooks

- Proposal Status: [wip](README.md#status)
- Issue Number: [233](https://github.com/sudoblockio/tackle/issue/233)
- Proposal Doc: [base-methods-as-hooks.md](https://github.com/sudoblockio/tackle/blob/main/proposals/base-methods-as-hooks.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

This proposal would allow setting literal values if the first arg is a default method - either `if`, `else`, `when`, or `for`. All other kwargs fail.


### Lists

```yaml
this: that
foo:
  - bar
  - ->: --if this=='that' baz

check: assert {{foo[1]}} baz
```

```yaml
foo:
  - bar
  - ->: --for [1,2,5] {{item}}

check: assert {{foo[1][1]}} 2
```

```yaml
foo:
  - bar
  - ->: --for [1,2,5] {{item}} --merge

check: assert {{foo[1]}} 1
```

See [#141](https://github.com/sudoblockio/tackle/issues/141)

### Maps

```yaml
this: that
foo:
  bar: baz  
  bing->: --if this=='that' bang  

check: assert {{foo[bing]}} bang
```
