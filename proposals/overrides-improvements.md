---
id:
title: Overrides Improvements
status: wip
description: Improve how overrides are tracked and applied when parsing files / hooks
issue_num: 247
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Overrides Improvements

Improve how overrides are tracked and applied when parsing files / hooks

- Proposal Status: [wip](README.md#status)
- Issue Number: [247](https://github.com/sudoblockio/tackle/issue/247)
- Proposal Doc: [overrides-improvements.md](https://github.com/sudoblockio/tackle/blob/main/proposals/overrides-improvements.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

Overrides are needed for testing as input fields need values inserted for testing.

- Overrides are different from kwargs
  - Difference
    - Overrides can be used within exec while kwargs are validated by function's interface  
    - Makes sense as kwargs can't be randomly used within exec -> they should be consumed and validated appropriately
    - Otherwise, they are the same?
    - kwargs get applied when calling the tackle file / function
    - overrides get carried into functions
  - Need to differentiate and track down where when parsing non-functions we override the key with a kwarg
- Should not be applying override when creating the function but when the dict is parsed thereby we have a singular way to apply the overrides regardless of whether we are in func or normal
- Can't just override keys as they might have a hook in them
- Overrides need to be brought into the function

> I think long story short, overrides should be assessed on each key. Right now overrides don't work when parsing the field context of dcl hooks. This is a pain as it makes us split up the logic


### Examples

**Override**
```yaml
foo:
  bar:
    baz: 1
```

**Input**
```yaml
foo:
  bar: 1
```


**Override**
```yaml
foo:
  bar:
    - null
    - 1
```

**Input**
```yaml
foo:
  bar:
    - 1
    - 2
```


## Command line

`tackle --foo baz`
- Extra vars come in as global_kwargs
- global_kwargs then turned into kwargs in `run_source`
- `run_source` runs `update_input_context_with_kwargs`
- For
  - Non-functions
    - kwargs then override keys in normal files (not consumed)
  - Functions
    - kwargs are consumed by function input fields

`tackle --override foo.yaml` + `tackle --override foo=baz`
- Override is put into override context


```yaml
foo: bar
foo->: bar
foo_>: bar
```

- Overrides individual keys

```yaml
f<-:
  foo: bar
  foo->: bar
```

- Sets the value of the field

```yaml
f<-:
  exec:
    foo: bar
    foo->: bar
    foo_>: bar
```

- Overrides the value field

## TTD

- [x] Remove the override to global_kwarg logic
- [x] New macro to expand:
  - function fields
  - context values
- [ ] Insert overrides into `create_function_model`
  - Really? -> Don't think so
- [ ] Overrides are now applied in two places
  - `walk_sync`
    - Can't be applied just on keys as `walk_sync` recurses into nested values and single level overrides should not be applied to nested values  
    - What would be better is if the overrides are applied before `walk_sync`
      - Normal file
        - `run_source`
  - `function_walk`
    - Same as above, should be applied in this function

