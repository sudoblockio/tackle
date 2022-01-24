# Development Roadmap

Tackle-box is still a work in progress with the following new features planned.

## Functions

Hooks are supposed to be written in an imperative language (ie python) though it would be good to have a declarative form of being able to call groups of hooks which could be called functions. Functions would have the same properties of hooks in that they will have arguments and parameters with types and defaults along with an exec method which is then run when the function is called. Functions will be extracted from the tackle file from keys with an arrow in the opposite direction of a hook (ie `<-` for public / `<_` for private) before it is parsed and then made available during the main parsing sequential run. Functions would be importable within providers so that providers can share reusable groups of logic.

For instance this could be an example of a function:

```yaml
function_example<-:
  args:
    - name: param1
    - name: param2
  kwargs:
    param1:
      type: str
    param2:
      type: list
      default: []
    param3:
      type: bool
      default: false
  exec:
    call1->: another_hook param1 param2
    call2->: another_hook call1 param3
  return: call2
```

Which could then be called like:

```yaml
a_list:
  - stuff
  - things
called from a hook->: function_example foo "{{ a_list }}"
called within a hook:
  ->: some_hook
  param: $function_example foo "{{ a_list }}"
```

Functions can then refer to other functions to also create nested logic.

## Help on Providers and Files

No CLI is complete without some kind of help screen that describes the actions that can be taken. Early thinking was that these help dialogues could be triggered by running a reserved parameter `help` when calling tackle.  For instance running `tackle robcxyz/tackle-provider help` should display what the provider is able to do. These help items should be both keys calling hooks with a `help` kwarg or public functions. The format should be similar to other help screens (ie calling `tackle --help`) and make the tool more of a declarative CLI.
