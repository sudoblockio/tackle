# Flow Control

### If Statements

```yaml
planet->: select What planet you on? --choices ['earth','mars']
weather:
  ->: print {{ planet | title }} weather is nice!
  if: planet == 'earth'
```

### Else

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

### When

`when` takes effect before for loops which `if` operates after.

```yaml
words: ['Hello', 'cruel', 'world!']
expanded:
  ->: print {{item}}
  for: words
  when: "'Hello' in words"
  if: item != 'cruel'
```

### For Loops

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

### For Loop Rendered

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

### For Loop Using [keys](../providers/context/keys.md) Hook

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

### List Comprehension

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

### Try / Except

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

### `merge`

```yaml
stuff: things

to merge->:
  merge: true
  stuff: more things
```

Results in:

```yaml
stuff: more things
```

### Blocks

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

```yaml
stuff: things
foo: bar

code->:
  # ...
  foo: baz
  inner-context->: "{{ foo }}"
  outer-context->: "{{ stuff }}"
```

### Match / Case

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
