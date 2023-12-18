# YAML Deficiencies


## Use with Special Keys

```yaml
# This will never work
foo: bar
print->: {{foo}}
return->: {{foo}}
```