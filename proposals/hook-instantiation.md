---
id: hook-instantiation
title: Hook Instantiation
status: wip
description: Open the concept of using methods on instantiated hooks
issue_num: 238
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

[//]: # (--end-header--start-body--MODIFY)


When calling methods, in the past we have opted for converging the fields of method into the base like this.

```yaml
hook<-:
  foo: str
  method<-:
    bar: str

h->: hook method --foo a --bar b
#h:
#  bar: b
#  foo: a
```

But that is really a macro version of this
```yaml
hook<-:
  foo:
    type: str
...
```

Which could also have properties that inform whether the the field is inherited.

```yaml
hook<-:
  foo:
    type: str
    passed: true
  method<-:
    bar: str

h->: hook method --foo a --bar b
#h:
#  bar: b
#  foo: a
```

And allow us to have more control over how the object is used.

```yaml
hook<-:
  foo:
    type: str
    passed: false  # Default could be true?
  method<-:
    bar: str

h->: hook method --bar b # This now complains no foo
```

But I think it also opens up the possibility of discriminating between a couple of things.

- an instantiated vs uninstantiated hook
- calling a method of a hook and calling a method on an existing hook

Both these concepts are related.

instantiated vs uninstantiated hook

We should be able to populate a hook and then call a method on it.

```yaml
hook<-:
  foo:
    type: str
    passed: true
  method<-:
    bar: str

h->: hook --foo a
g->: h method --bar b
```

But right now that is not possible for a couple reasons

- h is a dict, not a hook
- The only way to call `h` is if it was a hook
  - Right now it is only data and so h is going to throw
  - But what if it didn't? How would that look?

Options:
- Maintain another hook namespace of called hooks with methods.
  - If a hook has been called, it still exists in the hooks namespace and nothing should be done if it doesn't have any other methods
  -



