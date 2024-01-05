---
id: complex-types-use
title: Complex Type Use
status: wip
description: Using complex types has issues
issue_num: 228
blockers: []
---

[//]: # (--start-header--DO NOT MODIFY)

# Complex Type Use

Using complex types has issues

- Proposal Status: [wip](README.md#status)
- Issue Number: [228](https://github.com/sudoblockio/tackle/issue/228)
- Proposal Doc: [complex-type-use.md](https://github.com/sudoblockio/tackle/blob/main/proposals/complex-type-use.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

Currently we allow declaring types for fields within a declarative hook and can have those fields validated when the hook is called but can't create fields which are validated on assignment. This prevents creation of typed data types like `list[str]` or `list[Foo]` within a hook.  

### Examples

```yaml
F<-:
  foo: list
()<-:
  try_ok->: F --foo string --try --except ok
  ok->: F --foo ['string']
```

This is fine.

```yaml
F<-:
  foo: str
G<-:
  foo: int
H<-:
  bar:
    type: list[F]
<-:
  exec:
    # Technically not a list[F] but F into a list
    ok->: F --foo {{item}} --for ['a','b']
    try_ok->: G --foo {{item}} --for ['a'] --try --except ok

    # This is right
    h_ok:
      ->: H
      bar:
        - foo: bar
    h_try_ok:
      ->: H --try --except ok
      bar:
        - not foo: bar
#ok:
#- foo: a
#- foo: b
#try_ok:
#- ok
#h_ok:
#  bar:
#  - foo: bar
#h_try_ok: ok
```

These are the only ways to instantiate a `list[F]` with the first ways a hack, instantiating F into a list.

```yaml
F<-:
  foo: str
G<-:
  bar:
    type: dict[str, F]
<-:
  exec:
    ok:
      ->: G
      bar:
        a:
          foo: bar
    ok_merge:
      ->: G --merge
      bar:
        a:
          foo: bar
    try_ok:
      ->: G --try --except ok
      bar:
        a:
          not foo: bar
#ok:
#  bar:
#    a:
#      foo: bar
#bar:
#  a:
#    foo: bar
#try_ok: ok
```

Only way to do it with `dict[str, F]` is with an intermediary object.

There is no way to get rid of that intermediary object's key - `bar` in this case. For instance there is no way to achieve this output


```yaml
F<-:
  foo: str
G<-:
  bar:
    type: dict[str, F]
<-:
  exec:
    ok_merge:
      ->: G --merge
      bar:
        a:
          foo: bar
#ok_merge:
#  a:
#    foo: bar
```

### Instantiating Large Objects

```yaml
T<-:
  # Some large thing
  foo: bar

data:
  # Some large thing
  foo: baz

call_bad:
  ->: T --foo {{data.foo}} # ... Won't scale.
```

