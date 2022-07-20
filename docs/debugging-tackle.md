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

### Debugging the source

When writing hooks or in special scenarios when you need a proper debugger, you can set breakpoints within the parser source code or within each hook which is super helpful when writing hooks. This is should be a last resort if not writing your own custom hooks but





Every hook within tackle has some test that one can set breakpoints within with useful fixtures to gain entrypoints into all the business logic. The basic layout of every hook's test looks a similar to:

```python
def test_collections_hook_concate(change_dir):
    output = tackle('concatenate.yaml')
    assert output['out'] == ['foo', 'bar', 'stuff', 'things']
```

Using the pytest fixture `change_dir` which automatically changes the tests running context to the directory the test file is located, a yaml file is written that calls the hooks