# Using Providers

### From the command line

Providers can be called directly from the command line per the [calling tackle](command-line.md) documentation.

For instance:
```shell
tackle robcxyz/tackle-provider # Or https://github.com/robcxyz/tackle-provider
tackle path/to/dir/with/tackle/file
tackle path/to/tackle/file.yaml
tackle  # Checks in parent dir for tackle.yaml file
```

### Calling from tackle file

Within a tackle file, another provider can be called which would run the tackle file by calling the [tackle hook](providers/tackle/tackle.md). For instance:

```yaml
call another tackle->: tackle path/to/local/or/remote/provider
```

Note that at this time additional arguments / keys / flags do not work the same as when calling from the [command line](command-line.md#additional-arguments-keys-flags) and instead act like additional arguments / keys / flags for hooks and instead behave like [normal hook calls](writing-tackle-files.md#hook-call-forms).

See [issue #83](https://github.com/robcxyz/tackle/issues/83) for details about mapping unknown arguments.

### Importing hooks from a provider

Hooks can be imported from a tackle provider with the [import](providers/Tackle/import.md) hook. For instance in a tackle file:

```yaml
import_>: path/to/local/or/remote/provider
using that hook->: the_imorted_hook ...
```

Here we use a [private hook call](writing-tackle-files.md#public-vs-private-hook-calls) to import hooks as the output of this hook call is not needed.

