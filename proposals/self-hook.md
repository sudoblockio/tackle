---
id:
title: Self Hook
status: wip
description: Create a special `self` hook to reference the hook's methods during parsing
issue_num: 258
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Self Hook

Create a special `self` hook to reference the hook's methods during parsing

- Proposal Status: [wip](README.md#status)
- Issue Number: [258](https://github.com/sudoblockio/tackle/issue/258)
---
[//]: # (--end-header--start-body--MODIFY)

```yaml
MyHook<-:
  foo: bar
  a_method:
    bar: bar
  exec:
    get_a_method->: self a_method --merge
call->: MyHook --foo baz
```

```yaml
self<-:
  foo:
    type: str
    default: baz
#  ...
```

- Same as before but the instantiated type is now the default


#### `self` as Hook

If `self` was a hook it would be simple to implement but the issue is we need to know that we are inside a hook from the context, otherwise if `self` is called, within that hook it will not know that it is in fact executing within another hook. For instance:

```yaml
Foo<-:
  bar: baz
  Method<-: ...
  exec:
    do->: self Method
```

Inside `do` we don't know that we are within an `exec` of another hook. If we did know that, we could easily build the hook