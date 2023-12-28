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
name->: input What is your name? --default Arthur
check name:
  ->: print You may pass {{ name }}
  if: name == 'Arthur'
  else:
    raise->: Wrong name...
```

Which can also be rendered.

```yaml
check name:
  # ...
  else: "Hello {{name}}"
```

And could have hooks embedded in it.

```yaml
check name:
  # ...
  else: "{{print('Hello', name)}}"
```

And of course it can be expressed in a single line.

```yaml
name->: input What is your name?
hello->: print You may pass {{ name }} --if name == 'Arthur' ---else "{{print('Hello', name)}}"
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

### For Loops with Variable

The cleanest way to run a for loop is by declaring a variable within the loop

```yaml
loop:
  ->: var "i={{i}}"
  for: i in [1,3,5]
```

```yaml
loop:
- i=1
- i=3
- i=5
```

If multiple variables are declared for a list iterand, the first positional variable becomes the index.

```yaml
loop:
  ->: var "i={{i}} v={{v}}"
  for: i, v in [1,3,5]
```

```yaml
loop:
- i=0 v=1
- i=1 v=3
- i=2 v=5
```

This can also be done against objects

```yaml
an_object:
  foo: bar
  stuff: things
loop_one:
  ->: "k={{k}}"
  for: k in an_object
loop_two:
  ->: "k={{k}} v={{v}}"
  for: k, v in an_object
loop_three:
  ->: "i={{i}} k={{k}} v={{v}}"
  for: k, v, i in an_object
```

```yaml
an_object:
  foo: bar
  stuff: things
loop_one:
- k=foo
- k=stuff
loop_two:
- k=foo v=bar
- k=stuff v=things
loop_three:
- i=0 k=foo v=bar
- i=1 k=stuff v=things
```

### For Loops without Variable

If you don't give a variable (ie `i in an_iterand`) then the variable names are assumed depending on if you are iterating over a list or an object.

```yaml
loop:
  ->: "item={{ item }} index={{ index }}"
  for:
    - stuff
    - things
```

Would result in:

```yaml
loop:
- item=stuff index=0
- item=things index=1
```

Or for an object:

```yaml
loop:
  ->: "key={{ key }} value={{value}} index={{index}}"
  for:
    foo: bar
    stuff: things
```

```yaml
loop:
- key=foo value=bar index=0
- key=stuff value=things index=1
```

### For Loop Rendered

If the for loop value is a string, we attempt to render that by default (ie no braces).

```yaml
a_list:
  - stuff
  - things

printer:
  ->: print "We are at item {{ item }} and index {{ index }}"
  for: a_list
printer_compact->: print "{{ item }}/{{ index }}" --for a_list
```

### For Loop Using [keys](../providers/context/keys.md) Hook

```yaml
inputs:
  foo:
    type: stuff
  bar:
    type: things

printer:
  ->: var "The type is {{ inputs[item].type }}"
  for: "{{keys(inputs)}}"
```

```yaml
inputs:
  foo:
    type: stuff
  bar:
    type: things
printer:
- The type is stuff
- The type is things
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



