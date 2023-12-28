# Prompting

Tackle allows for a rich set of prompting options using the following hooks:

- [`input`](../providers/Prompts/input.md) - Text input for strings
- [`confirm`](../providers/Prompts/confirm.md) - Binary input for booleans
- [`select`](../providers/Prompts/select.md) - A selector of choices
- [`checkbox`](../providers/Prompts/checkbox.md) - A multi-selector of choices

There are other types of prompts such as [`editor`](../providers/Prompts/editor.md) and[`password`](../providers/Prompts/password.md) which are specialized versions of the [`input`](../providers/Prompts/input.md) hook that will not be covered in this document.

### Multi-line Prompting

Prompt hooks can be expressed in [expanded form](../writing-tackle-files.md#hook-call-forms).

```yaml
confirm hook:
  ->: confirm
  message: A confirm message
  default: false
input hook:
  ->: input
  message: An input message
  default: stuff
select hook:
  ->: select
  message: A select message
  choices:
    - stuff
    - things
checkbox hook:
  ->: checkbox --checked
  message: A checkbox message
  choices: [ 'stuff','things' ]  
```

**output**

```text
? A confirm message No
? An input message stuff
? A select message stuff
? A checkbox message
❯ ◉ stuff
  ◉ things
```

### Single-line Prompting

They can also be expressed in [compact form](../writing-tackle-files.md#hook-call-forms)
.

```yaml
confirm hook->: confirm A confirm message --default false
input hook->: input An input message --default stuff
select hook->: select A select message --choices ['stuff','things']
checkbox hook->: checkbox A checkbox message --choices ['stuff','things'] --checked
```

**output**

```text
? A confirm message No
? An input message stuff
? A select message stuff
? A checkbox message
❯ ◉ stuff
  ◉ things
```

### Embedded with Jinja Prompting

Prompt hooks can be embedded in one another.

```yaml
confirm + input hook->: input A message --if "confirm('Confirm this?')"
input + select hook->: input "A message with param={{select('A param',choices=['stuff','things'])}}"
```

**output**

```text
? Confirm this? Yes
? A message
? A param stuff
? A message with param=stuff
```

### Input Options

The [`input`](../providers/Prompts/input.md) hook can be expressed with some options.

```yaml
input-minimal->: input
input-compact->: input "What stuff?"
input-expanded:
  ->: input
  message: "What stuff?"
  default: things
```

```text
? input-minimal >>>  
? What stuff?  
? What stuff?  things
```

**Resulting Context**

```yaml
input-minimal: <user input>
input-compact: <user input>
input-expanded: things
```

### Checkbox / Select Choice Inputs

The [`select`](../providers/Prompts/select.md) and [`checkbox`](../providers/Prompts/checkbox.md) are very similar with the following examples applying to both.

#### List Choice

Choice inputs can be a list and be rendered from an existing key.

```yaml
selection:
  ->: select
  message: A message
  choices:
    - stuff
    - things

a_list:
  - stuff
  - things

selection rendered:
  ->: checkbox
  message: A message
  choices: a_list
```

**output**

```text
? A message stuff
? A message
❯ ○ stuff
  ○ things
```

#### Prompt Display with Different Output

Choices can also be in the form of a list of maps with the keys being the displayed prompts and the values as the output of the selection.

```yaml
a_map:
  - a string: stuff
  - a map:
    stuff: things
  - a list:
      - stuff
      - things

selection:
  ->: select
  choices: a_map

# Or in compact form
# selection->: select --choices a_map
```

```text
? selection >>>
❯ ○ a string
  ○ a map
  ○ a list
```

The output of the hook in this case would be `foo`, `{'bar':'baz'}`, or `['stuff','things']` depending on the selection.

#### List Keys Map Choice

Sometimes it is convenient to extract the keys from a map as choices which can then be used elsewhere to index the map. In this case we use the [`keys`](../providers/Context/keys.md) hooks to extract a list of keys from a map.

```yaml
a_map:
  stuff: foo
  things: bar

selection->: select --choices keys(a_map)
print value->: print {{a_map[selection]}}

# Or as a single liner
print value single line->: print {{a_map[select(choices=keys(a_map))]}}
```

#### Checkbox Default

The default of the [`checkbox`](../providers/Prompts/checkbox.md) hook is that nothing is selected but it is possible for all the values to selected as the default.

```yaml
checker->: checkbox --choices ['stuff','and','things'] --checked
```

```text
? checker >>>
❯ ◉ stuff
  ◉ and
  ◉ things
```

**Resulting in**

```yaml
checker:
  - stuff
  - and
  - things
```
