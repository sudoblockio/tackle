---
id:
title: Exec Method Arrows
status: wip
description:
issue_num: 248
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

[//]: # (--end-header--start-body--MODIFY)

# Private + Bare `exec` Method (ie `exec<_` / `exec`)

The `exec` method on a declarative hook is special in that when it exists, the return of the hook is public data from parsing it. This is how we can make dcl hooks into functions with typed inputs. For example:

```yaml
a_hook<-:
  foo: bar
  exec:
    stuff: things

run_hook->: a_hook
assert->: a_hook {'stuff':'things}
```

Currently, when processing this method, we run a macro such that the field `exec` is transformed to `exec<-` which is a public method. If an `exec` method exists, then only the public data from the `exec` execution is returned as is shown in the above example (ie {'stuff': 'things'}).

This proposal opens up the idea of what various `exec` methods behave when called bare (`exec`), publicly (`exec<-`), and privately (`exec<_`). It is centered around the notion of what happens to the fields in the hook in response to various `exec` methods.

## Proposal

There are three general options which are possible with the following outcomes.

- Bare `exec` -> Returns on the public data
- Public method `exec<-` -> Returns the fields along with the public data
- Private method `exec<_` -> Returns only the fields and none of the exec method
- Public hook call `exec->` -> Call as if it is a hook
- Private hook call `exec_>` -> Call as if it is a hook with --no_output

Values of different types can be used as well.

- Dict bare + methods -> walk
- Dict hook call -> block  
- String bare + methods ->

### Examples

#### Bare

Only the `exec` method's public data.

```yaml
a_hook<-:
  foo: bar
  exec:
    stuff: things

expected_output:
  stuff: things

assert->: {{a_hook()}} {{expected_output}}
```

#### Public

Both the `exec` method's public data and the fields.

```yaml
a_hook<-:
  foo: bar
  exec->:
    stuff: things

expected_output:
  foo: bar
  stuff: things

assert->: {{a_hook()}} {{expected_output}}
```


#### Private

Only the field's data.

```yaml
a_hook<-:
  foo: bar
  exec_>:
    stuff: things

expected_output:
  foo: bar

assert->: {{a_hook()}} {{expected_output}}
```
