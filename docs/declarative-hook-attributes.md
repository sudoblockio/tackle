
> WIP 

Validators
Extends
Overrides 
Config
Alias
Return
Remove


### Validators

Validators are functions that are run when a field is set and require returning the value to set the field. 

Validators can be set at the hook definition level or within a field itself. When defining validators on a hook definition level, an object with keys regex matched to field names is expected allowing users to apply validators to multiple fields at the same time.

The shorthand version of validators leverages a macro to assume variable names when asserting logic where the value being validated 

**Shorthand Validator**
```yaml
SomeHook<-: 
  foo: bar
  validators: 
    foo:  # Apply validator to field `foo`
      assert->: isinstance(v,'str')
      return->: baz --if v=='bar'
```

**Regex Matching Case**
```yaml
SomeHook<-: 
  foo: bar
  baz: bing 
  validators: 
    foo|baz: 
      assert->: isinstance(v,'str')
      return->: baz --if v=='bar'
```

```yaml
SomeHook<-: 
  foo: 
    default: bar
    validator:
      assert->: isinstance(foo,'str')
      return->: baz --if v=='bar'
```

```yaml
SomeHook<-: 
  foo: 
    default: bar
    validator:
      values:
        v: bar 
        info: ...
      mode: 
      body:
        assert->: isinstance(foo,'str')
        return->: baz --if v=='bar'
```
### Extends 

Hooks can extend other hooks allowing inheritance patterns to keep hook implementations dry. Hooks that are extended inherit both their base fields and methods all of which can be overriden within the definition. 

```yaml
BaseHook<-:
  foo: bar 
  baz: bing
  
  output<-: 
    return->: "{{foo}}"
  
ExtendedHook<-:
  extends: BaseHook 
  baz: bang 
assert->: "{{BaseHook.foo}}" "{{ExtendedHook.output}}"
```

You can also extend from multiple hooks. Fields are inherited in order with the last item  


### Overrides 


### Config

Hooks can have configuration properties the same as [pydantic's]() to inform how the hook validates it's fields and other aspects of model instantiation. 

