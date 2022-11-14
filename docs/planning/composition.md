# Composition

> Not Implemented

Would be good if a declarative hook field was able to be typed like another hook would be. This would allow nesting of typed structures as is common in many schema oriented operations.

### Examples

```yaml
Foo<-:
  input_str: str

Bar<-:
  foo: Foo

p->: {{Bar(foo=Foo(input_str='fooo'))}}
```

Expected output

```yaml
p:
 foo:
   input_str: fooo
```

## Implementation

- Issue right now is that fields, after being instantiated, are not exported properly as serializable types since they have not been necessarily called. Even if they are called in a recursive way, can't get the field to replace the existing typed field.  

- [x] Add typed field in function init
- [ ] Make composed fields usable as output
