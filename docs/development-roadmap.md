# Development Roadmap

Tackle-box is still a work in progress with the following new features planned.

- [Help on Providers and Files](#help-on-providers-and-files)
- [IDE Autocomplete](#ide-autocomplete)
- [Providers allowing import of jinja extensions](#providers-allowing-import-of-jinja-extensions)

## Help on Providers and Files

No CLI is complete without some kind of help screen that describes the actions that can be taken. Early thinking was that these help dialogues could be triggered by running a reserved parameter `help` when calling tackle.  For instance running `tackle robcxyz/tackle-provider help` should display what the provider is able to do. These help items could be:

- Keys calling hooks with a `help` kwarg
- Public functions

The format should be similar to other help screens (ie calling `tackle --help`) and make the tool more of a declarative CLI.

If this happens, a reserved key could exist that would be the default action when calling the provider. For instance calling `tackle robcxyz/tackle-provider help` with this in the context:

```yaml
->:
  help: This would be the providers general help section
```

Could further enrich a help screen with general provider information. Since the default behavior when running the hook is just to parse the whole file, wouldn't make sense to have this hook do anything more unless that is advantageous.  Need users input to make that call.  

## IDE Autocomplete

Need to extract the json schema from each hook and upload that to [schemastore.org/json/](https://www.schemastore.org/json/) with appropriate [catalog.json](https://www.schemastore.org/api/json/catalog.json) file.

## Providers allowing import of jinja extensions

Providers give a good import abstraction so it would be cool to be able to allow dynamically importing of various jinja extensions as well.
