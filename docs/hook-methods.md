# Hook Base Methods

Every hook has a number of base methods that are implemented alongside the declaration of the hook.  This document outlines each of these methods with an example of their use.

- [Conditionals](#conditionals)
    - `if` / `else`
- [Loops](#loops)
    - `for` / `reverse`
- [Methods](#methods)
    - `chdir`
    - `merge`
    - `try` / `except` - Coming soon
    - `defer` - Coming soon
    - `callback` - Coming soon

## Conditionals

Hooks can be conditionally called with an `if` key that needs to resolve to some kind of boolean. It is typically based on some kind of jinja expression. For instance:

```yaml
name->: input What is your name?
hello:
  ->: print Hello {{ name }}!
  if: name != 'Rob'
```

Here we can see the `if` key that by default is wrapped with jinja braces and is evaluated as true or false depending on the value entered into the `name` key. Full jinja syntax is supported so other assertions such as whether an item is in a list (ie `if: 'a key' in a_list`) is supported.

If you want to return a different value when the `if` condition resolves to false, use the `else` key with the value you wish to return otherwise.  For instance:

```yaml
name->: input What is your name?
hello:
  ->: print Hello {{ name }}!
  if: name != 'Rob'
  else: Hello me
```

> Currently only returning static values is supported which might change in the next versions of tackle-box which could parse the `else` key for hooks.

## Loops

Hooks can be called in a loop based on specifying a list input in a `for` key and will always return a list to the key. Within the loop, the iterand is stored in a temporary variable `item` along with it's indexed position in a variable called `index`. For instance running:

```yaml
printer:
  ->: print "We are at item {{ item }} and index {{ index }}"
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
a_list_>:  # This is a private key now and won't be part of the output context
  - stuff
  - things

printer:
  ->: print "We are at item {{ item }} and index {{ index }}"
  for: a_list
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

## Methods

### `chdir`

Sometimes it is desirable to run the hook in another directory.  For this there is the `chdir` key where the hook is called in the context of the directory being specified. For instance one could run the `listdir` hook in another directory:

```yaml
contents:
  ->: listdir
  chdir: path/to/some/dir
```

### `merge`

If the output of the hook call is a map, then one can merge that map into the parent keys.  For instance given this [`block` hook]():

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

### `try` / `except` - Coming soon
### `defer` - Coming soon
### `callback` - Coming soon
