---
id: hook-field-validators
title: Hook Field Validators
status: implemented
description: Validate fields with custom logic similar to pydantic's validation
issue_num: 241
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Hook Field Validators

Validate fields with custom logic similar to pydantic's validation

- Proposal Status: [implemented](README.md#status)
- Issue Number: [241](https://github.com/sudoblockio/tackle/issue/241)
---
[//]: # (--end-header--start-body--MODIFY)

## Examples

Simple example where we have an if and return.

```yaml
H<-:
  foo:
    type: str
    default: bar
    validator:
#      fields:
#        v: Any
#        info: FieldValidationInfo
      fields: ['v', 'info']
      mode:
        enum: ['before', 'after', 'wrap', 'plain']
        default: after  
      body:
        assert->: "{{isinstance(v, 'str')}}"
        return->: v
```

```yaml
H<-:
  foo:
    type: str
    default: bar
  validators:
    foo:
      assert->: "{{isinstance(v, 'str')}}"
      return->: v
```




```yaml
validator:
  return->: v --if type(v) == 'str' --else raise Wrong type
```

```yaml
FieldValidationInfo<-:
  data:
    type: Context
    default->: var public_context
  context:
    type: union[Context]
    default->: var public_context
  Config<-:
    args: ['data', 'context']  
```


### Old

```yaml
H<-:
  foo:
    type: str
    default: bar
    validators:
      - if: foo is None
        return: ''
      - if: not type(foo, 'str')
        return: ''
      - if: not regex_match(foo, '^[a-zA-Z]')
        return: ''
    validator:
      if: foo is None
      return: ''
```

```yaml
H<-:
  type:
    enum:
      - int32
      - int64
    validator:
```

```yaml
validator:
  if:
  return:
```



```yaml
validator:
  field:
    type: str
    default: v
  info:
    type: FieldValidationInfo
    default: info
  init:
    <-:
      exec:
        var: var var --if var!='item'  
        values: var var --if values!='values'  
  exec:
```