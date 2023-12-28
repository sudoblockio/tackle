# The `block` and `match` Hooks

There are two important hooks that users should be aware of, `block` and `match`.

- [`block`](../providers/Tackle/block.md) - Hook for wrapping objects with flow control and / or reindexing the data so that nested variables don't need to be referenced from the root
- [`match`](../providers/Logic/match.md) - For `match` / `case` statements which again can have reindexed data

### Blocks

Here we have an example of some input data (`action`) who's output determines what block of data to parse.

```yaml
action:
  ->: select What are we doing today?
  choices:
    - code: Code tackle stuff
    - do: Do things

code->:
  if: action == 'code'
  # Run a number of hooks conditional on the `action`
  arbitrary:
    contex: ...
  gen->: tackle robcxyz/tackle-provider
  open->: command touch code.py
  # ...

do->:
  if: action == 'do'
  check_schedule->: webbrowser https://calendar.google.com/
  # ...
```

### Block Render Context

Another use of blocks is to allow referencing of variables within an object without having to pass a full path to the variable as the data is indexed to the block start.

```yaml
stuff: things
foo: bar

code->:
  # ...
  foo: baz
  inner-context->: "{{ foo }}"
  outer-context->: "{{ stuff }}"
```

```yaml
stuff: things
foo: bar
code:
  foo: baz
  inner-context: baz
  outer-context: things
```

### Match / Case

Tackle supports `match` / `case` statements

```yaml
action:
  ->: select What are we doing today?
  choices:
    - Do stuff: stuff
    - Do things: things

run_action:
  ->: match action
  case:  
    stuff: Doing things
    things: Doing stuff
```

Which can also have hooks and indexed data

```yaml
run_action:
  ->: match select(choices=['stuff','things'])
  case:
    stuff->:
      foo: bar
      baz->: "{{foo}}"
    things->: literal things
```

Which can also have a default denoted by a `_`

```yaml
run_action:
  ->: match select(choices=['foo','does-not-exist'])
  case:
    foo: bar
    _: a default
```
