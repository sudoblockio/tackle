# Debugging

Debugging is somewhat rudimentary at this stage of tackle-box but there are some options to for both debugging tackle files and hooks.  

1. Printing the context
2. The [debug](providers/Tackle/debug.md) hook
3. Debugging the source

### Printing the context

If you are not interested in what is going on in the middle of the parser, the easiest way to see what values have been set at the end is to run tackle with the `--print` flag or `-p` in short. The output is then a json which can be further cleaned up with [jq]() like so.

```shell
tackle -p | jq -r
```

Note this only shows the [public context](memory-management.md#public-vs-private-context).

Additionally, tackle can print in yaml and toml formats. For instance using the `print-format` option,

```shell
tackle target -pf yaml
tackle target --print-format yaml
```

### The debug hook

Similar to setting a breakpoint, tackle has the ability to pause the parser and show the context at a given line. For instance:

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

Allowing users to debug tackle files by showing what is in each [memory space](memory-management.md).

See the [testing providers](testing-providers.md) document for testing providers with pytest.
