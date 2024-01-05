---
id: method-properties
title: Method Properties
status: wip
description: Methods could have properties which inform their behaviour
issue_num: 242
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Method Properties

Methods could have properties which inform their behaviour

- Proposal Status: [wip](README.md#status)
- Issue Number: [242](https://github.com/sudoblockio/tackle/issue/242)
- Proposal Doc: [method-properties.md](https://github.com/sudoblockio/tackle/blob/main/proposals/method-properties.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

It would be helpful if we could expose the control of how methods operated with parameters such as:

- `merge` - Informs if the method's output is merged into the top level keys - the default behaviour. False would keep the data under the method name (see below).
- `try` / `except` - Wrap method with try accept
- `for` - Run the method on some loop
- ?

Example - merge:
```yaml
MyHook<-:
  foo: bar
  my_method:
    <-:
      bar: baz
    merge: False

expected_output:
  foo: bar
  my_method:
    bar: baz

assert->: |
  {{MyHook.my_method()}} {{expected_output}}
```

This should not be super hard to implement as methods are just hooks which can have hook_call parameters which can be injected in. Only issue is the merge functionality needs to be modified or rethought since right now it is the default. So in the future that will need to be parameterized.  
