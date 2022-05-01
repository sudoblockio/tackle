# Debugging

Currently tackle has no way of debugging like a traditional language would by setting breakpoints within tackle files. Hopefully this will change in the future but until that happens, rudimentary debugging can be done by inserting `debug` hooks into tackle-files to see what the parser can see at a given point in a document.

For instance:

```yaml
stuff: things
public->: var stuff
private_>: var stuff
d->: debug
```

Would show:

```text
Public Context
{'public': 'things', 'stuff': 'things'}
Private Context
{'private': 'things'}

? CONTINUE  (Y/n)
```

Allowing users to debug tackle files by showing what is in each memory space.
