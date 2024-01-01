---
id: complex-types
title: Complex Types
status: implemented
description: Declaring hooks as types
issue_num: 229
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

[//]: # (--end-header--start-body--MODIFY)


# Complex Types

Would be good if a declarative hook field was able to be typed like another hook would be. This would allow nesting of typed structures as is common in many schema oriented operations.

### Examples

```yaml
Foo<-:
  input_str: str

Bar<-:
  foo:
    type: Foo

p->: {{Bar(foo=Foo(input_str='fooo'))}}
```

Expected output

```yaml
p:
 foo:
   input_str: fooo
```


##### Embedded

```yaml

Bar<-:
  foo:
    type: Foo

  Foo<-:
    input_str: str

bar:
  foo:
    input_str: fooo

p->: {{Bar(**bar)}}
```

Expected output

```yaml
p:
 foo:
   input_str: fooo
```

# Composition Types

### Complex Types

```yaml
Base<-:
  field: str

S<-:
  field1:
    type: Base
  field2:
    type: list[Base]
  field3:
    type: dict[str,Base]
  field4:
    type: optional[Base]
  field5:
    type: union[Base, str]
  field6:
    type: optional[Base]
  field7:
    type: optional[Base]
  field8:
    type: optional[Base]
  field9:
    type: optional[Base]
  field10:
    type: optional[Base]
```


### Enum

```yaml
Schema<-:
  with_type:
    type: string
    enum:
      - red
      - green
      - blue

  without_type:
    enum:
      - red
      - green
      - blue

  with_default:
    type: string
    default: red
    enum:
      - red
      - green
      - blue

  # Type can be inferred
  with_default_without_type:
    default: red
    enum:
      - red
      - green
      - blue
```

- Default is generally required as it makes little sense to require an input as an enum. Usually this should be set for you. Regardless, there needs to be a field that initializes the enum and default is as good as any.
- Alternatively we could simply specify an enum key as the input which will qualify the input.

```yaml
S<-:
  field:
    enum:
      - red
      - green
```

- Fields can also have different names than values which will be difficult to reason with potentially

```yaml
S<-:
  field:
    enum:
      red: 1
      green: 2
```

  - In this case, we would need to set the field by name, ie `red`, and then the output of the field would be `1`.


## Implementation

- Issue right now is that fields, after being instantiated, are not exported properly as serializable types since they have not been necessarily called. Even if they are called in a recursive way, can't get the field to replace the existing typed field.  
- Need to instantiate all the methods

## Implementation

- Issue right now is that fields, after being instantiated, are not exported properly as serializable types since they have not been necessarily called. Even if they are called in a recursive way, can't get the field to replace the existing typed field.  
- Need to instantiate all the methods

- [ ] Parse type
- [ ] Instantiate field as type