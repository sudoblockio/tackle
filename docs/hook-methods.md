# Hook Base Methods

Every hook has a number of base methods that are implemented alongside the declaration of the hook.  This document outlines each of these methods with an example of their use.

- [Loops](#loops)
    - `for` / `reverse`
- [Conditionals](#conditionals)
    - `if` / `when` / `else`
- [Methods](#methods)
    - `chdir`
    - `merge`
    - `try` / `except`
    - `defer` - Coming soon

## Loops

Hooks can be called in a loop based on specifying a list input in a `for` key and will return a list. Within the loop, the iterand is stored in a temporary variable `item` along with it's indexed position in a variable called `index`. For instance running:

```yaml
printer:
  ->: var "We are at item {{ item }} and index {{ index }}"
  for:
    - stuff
    - things
```

Would result in:

```yaml
printer:
  - We are at item stuff and index 0
  - We are at item things and index 1
```

The `for` key must be a list so if the input is a string, it is rendered by default like in this example which does the same as above:

```yaml
a_list:
  - stuff
  - things

printer:
  ->: print "We are at item {{ item }} and index {{ index }}"
  for: a_list
printer_compact->: print "{{ item }}/{{ index }}" --for a_list
```

Loop iterands can be of any type as in this example:

```yaml
printer:
  ->: print "The type is {{ item.type }}
  for:
    - name: foo
      type: stuff
    - name: bar
      type: things
```

Additionally, jinja hooks can be used to do some logic that could help with some patterns. For instance the [keys](https://sudoblockio.github.io/tackle/providers/Context/keys/) hook can be used to create a list of keys from a map which can be used as an iterand.

```yaml
inputs:
  foo:
    type: stuff
  bar:
    type: things

printer:
  ->: print "The type is {{ inputs[item].type }}
  for: "{{keys(inputs)}}"
```

### `reverse`

To loop through a list in reverse, simply set a `reverse` key to true as in this example:

```yaml
printer:
  ->: print "We are at item {{ item }} and index {{ index }}"
  for:
    - stuff
    - things
  reverse: true
```

Would result in:

```yaml
printer:
  - We are at item things and index 1
  - We are at item stuff and index 0
```

## Conditionals

### `if`

Hooks can be conditionally called with an `if` key that needs to resolve to some kind of boolean. It is typically based on some kind of jinja expression. For instance:

```yaml
planet->: select What planet you on? --choices ['earth','mars']
weather:
  ->: print {{ planet | title }} weather is nice!
  if: planet == 'earth'
```

Here we can see the `if` key that by default is wrapped with jinja braces and is evaluated as true or false depending on the value entered into the `planet` key. Full jinja syntax is supported so other assertions such as whether an item is in a list (ie `if: 'a key' in a_list`) is supported.

The `if` key is evaluated after a `for` loops are entered allowing list comprehensions to be done. For instance this example would only print "Hello world!".

```yaml
words:
  - Hello
  - cruel
  - world!
expanded:
  ->: print {{item}}
  for: words
  if: item != 'cruel'
compact->: print {{item}} --for words --if "item != 'cruel'"
```

### `when`

For imposing conditionality before a loop, the `when` method exists. For instance in this example the `when` is evaluated first, the loop is entered, and then the `if` condition is imposed to do a list comprehension.

```yaml
words: ['Hello', 'cruel', 'world!']
expanded:
  ->: print {{item}}
  for: words
  when: "'Hello' in words"
  if: item != 'cruel'
```

### `else`

If you want to return a different value when the `if` or `when` condition resolves to false, use the `else` key with the value you wish to return otherwise.  For instance:

```yaml
name->: input What is your name?
hello:
  ->: print Hello {{ name }}!
  if: name != 'Rob'
  else: Hello me
```

Which can also be rendered.

```yaml
intro: Hello
...
  else: {{intro}} me
```

And could have hooks embedded in it.
```yaml
hello:
...
  else: {{print('Hello me')}}
```

Or simply could be a dictionary output with further hooks.
```yaml
hello:
...
  else:
    stuff:
      things->: print foo
```

> Currently only jinja hooks are supported as string values. Future could add support for `else->/else_>` compact hook calls.

> Checkout the [match](https://sudoblockio.github.io/tackle/providers/Logic/match/) hook if needing to do a lot of conditionals which can satisfy regexes when catching cases.

## Methods

### `chdir`

Sometimes it is desirable to run the hook in another directory.  For this there is the `chdir` key where the hook is called in the context of the directory being specified. For instance one could run the `listdir` hook in another directory:

```yaml
contents:
  ->: listdir
  chdir: path/to/some/dir
```

### `merge`

If the output of the hook call is a map, then one can merge that map into the parent keys.  For instance given this [`block` hook](https://sudoblockio.github.io/tackle/providers/Tackle/block/):

```yaml
stuff: things

to merge->:
  merge: true
  stuff: more things
```

Would result in:

```yaml
stuff: more things
```

> Future work will support merging operations for lists as interpreted as an append operation

### `try` / `except`

To catch errors, use the `try` method which also can run a context in the case of failure in an `except` method.  For instance in both these example the print would execute.

```yaml
a failed command->: command "foo bar" --try  # Would exit without try
p->: print Hello world!  # This would print
```

```yaml
a failed command:
  ->: command "foo bar"
  try: true
  except:
    p->: print Hello world!
```

### `defer` - Coming soon

Future versions of tackle fill have a `defer` functionality similar to Go where one can declare deferred actions that will run if there is a script error or when a tackle file / execution is finished.  Details still [being worked out](https://github.com/robcxyz/tackle/issues/37).
