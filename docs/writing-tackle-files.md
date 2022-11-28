# Tackle File Parsing Logic

This document aims to provide an overview of the core parsing logic for tackle files which are arbitrary yaml files that have hooks embedded in them.

## Basics

Tackle **sequentially** parses **arbitrary** json or yaml files with the parser only changing the data structure when hooks are called denoted by forward arrows, ie `->`/`_>` at the end of a key / item in a list. Hooks can perform a variety of different actions such as prompting for inputs, making web requests, or generating code and return values that are stored in the key they were called from. After any key / value / item in a list is parsed, it is available to be referenced / reused in additional hook calls through jinja rendering.

### Hook Call Forms

Hooks can be called in directly in expanded and compact forms or within jinja as an extensions or filters. For instance running:

**`example.yaml`**
```yaml
expanded:
  ->: input
  message: Say hello to?
compact->: input Say hello to?
# Or with jinja
jinja_expression->: "{{input('Say hello to?')}}"
```

Which when run with `tackle docs/scratch.yaml -pf yaml`:

```text
? Say hello to? Alice
? Say hello to? Bob
? Say hello to? Jane
```

Results in the following context:

```yaml
expanded: 'Alice'
compact: 'Bob'
jinja_expression: 'Jane'
```

In this example we are calling the [input](providers/Prompts/input.md) hook that prompts for a string input which has one mapped argument, `message`, which in the compact form of calling [input](providers/Prompts/input.md) allows it to be written in a single line. The exact semantics of how arguments are mapped can be found in the [python hooks](python-hooks.md) and [declarative hooks](declarative-hooks.md) documentation.

The [input](providers/Prompts/input.md) hook has several parameters that are not mapped as arguments such as `default` which can be used in both expanded and compact forms but not in jinja which relies on [mapped arguments](python-hooks.md#arguments-with-list-and-dict-types). For instance:

```yaml
expanded:
  ->: input
  message: Say hello to?
  default: world
# Equivalent to
compact->: input Say hello to? --default world
# Notice the additional argument
print->: print Hello {{compact}} Hello {{expanded}}
```

### Control Flow

Tackle also enables conditionals, loops, and other [base methods](hook-methods.md) that are also able to be expressed in both hook call forms.  For instance here we can see a `for` loop in both forms:

```yaml
ttd:
  - stuff
  - and
  - things

expanded:
  ->: input
  for: ttd  # Strings are rendered by default for `for` loops
  message: What do you want to do?
  default: "{{item}}" # Here we must explicitly render as default could be a str
# Equivalent to
compact->: input What do you want to do? --for ttd --default "{{ item }}"
```

For more information on loops and conditional, check out the [hook methods documentation.](hook-methods.md)

### Public vs Private Hook Calls

Thus far all the examples have been of public hook calls denoted by `->` arrows which run the hook and store the value in the key but sometimes you might want to call hooks but not have the key stored in the output. To do this you would instead run a private hook denoted by `_>` arrow.  Such cases exist when you are dealing with a strict schema and want to embed actions / logic in that schema or you want to keep a clean context and ignore the output of a key. The output of a private hook call is still available to be used later in the same context and is only removed when the context changes such as when a tackle hook is called that parses another tackle file / provider.

For more information, check out the [memory management](memory-management.md) docs.

## Special Cases

While all logic can be expressed simply through calling hooks, several convenient shorthand forms exist for calling common hooks such as `var` for rendering a variable and `block` for parsing a level of the input.  

### Rendering Variables

Values / keys are not rendered by default but instead need to be rendered through a hook call. To make this easier, a special case exists where if the value of a hook call is wrapped with braces (ie `key->: "{{ another_key }}"`) it is recursively rendered right away. For instance:

```yaml
a_map:
  stuff: things
reference->: "{{ a_map }}"
```

Would result in:

```yaml
a_map:
  stuff: things
reference:
  stuff: things
```

This allows creation of renderable templates in keys that one can reuse depending on what the current context is.  For instance:

```yaml
stuff: things
a_map:
  more-stuff: "{{ stuff }}"
reference->: "{{ a_map }}"
```

Would result in:

```yaml
stuff: things
a_map:
  more-stuff: "{{ stuff }}"
reference:
  stuff: things
```

### Blocks

Sometimes it is convenient to be able to apply logic to entire blocks of yaml for which there is a special case embedded in the parser. For instance, it is common to use a single / multi selector in a tackle file to restrict users to running a certain set of functions:

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

If this example was run, the user would be prompted for a selection which based on their input, the block of code hooks would be executed based on the `if` condition.  Under the hood the parser is re-writing the input to execute a `block` hook like this example though the code above makes it simpler:

```yaml
code:
  ->: block
  if: action == 'code'
  items:
    arbitrary:
      contex: ...
    gen->: tackle robcxyz/tackle-provider
    open->: command touch code.py
```

#### Block render context

When writing blocks, one has access to two different render contexts, a local block context which is referenced and the outer global context.  For instance:

```yaml
stuff: things
foo: bar

code->:
  # ...
  foo: baz
  inner-context->: "{{ foo }}"
  outer-context->: "{{ stuff }}"
```

In this example, the key "inner-context" would equal "baz" while the "outer-context" is able to reference "stuff".

Check the [memory management docs](memory-management.md) for more information on different contexts.

#### Side note on blocks - Try out `match` hooks

For another way of conditionally parsing blocks of yaml, checkout the [`match` hook]() which performs similarly to match / switch case statements per the below example.

```yaml
action:
  ->: select What are we doing today?
  choices:
    - code: Code tackle stuff
    - do: Do things

run_action:
  ->: match
  value: "{{ action }}"
  case:  
    code:
      gen->: tackle robcxyz/tackle-provider
      # ...

    do:
      if: action == 'do'
      check_schedule->: webbrowser https://calendar.google.com/
      # ...
```

Check out the [declarative hooks](declarative-hooks.md) docs for patterns on how you can wrap this logic with reusable interfaces.

