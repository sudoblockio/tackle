

> Blocked by [return-hook](return-hook.md)

Currently when a declarative hook is called with an exec, the entire context is parsed with a special field for returning the appropriate value (`return`) being used to specify what the result is of that parsing.

This proposal would modify the parsing behaviour so that special keys can be used to indicate whether a variable  is returned.

## Examples

Normal parsing
```yaml
foo: bar
return->: return {{foo}}
```


## Macros

```yaml
foo: bar
return->: return {{foo}}
```

Then move to using return hook.
```yaml
foo: bar
tmp:
  ->: return {{foo}}
```
