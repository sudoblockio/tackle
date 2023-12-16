# Jinja

At the core of all tackle logic is the jinja templating language which enables the majority of the features in the syntax.

## Variable

By default, all fields in tackle hooks are rendered if they have curly braces. For instance given the following hook call, the output would print `stuff` then `things`:

```yaml
stuff: things
string->: print stuff
jinja->: print {{stuff}}
```

## For Loops

When running within a for loop, tackle automatically keeps track of the iterand and integer index of the loop. For instance the following would print out `stuff 0` and `things 1`:

```yaml
printer:
  ->: print {{item}} {{index}}
  for:
    - stuff
    - things
```

Alternatively that could be written as:

```yaml
printer->: print {{item}} {{index}} --for ['stuff','things']
```


## Rendering By Default

Not all fields need to be wrapped with jinja though including several base methods and hook fields. For instance the `if` and `for` methods are automatically interpreted as jinja expressions and do not need to be wrapped with braces. This is because writing an `if` statement makes little sense unless it is dynamic which jinja is needed for. Along the same thread, inputs of type string for `for` loops implicitly mean they need to be rendered. For instance the following would print out `stuff` and `things`.

```yaml
a_list:
  - stuff
  - things
printer:
  ->: print {{item}}
  if: "'stuff' in a_list"
  for: a_list
```

> Note the additional quotes in the if statement which is a yaml parsing nuance of ruamel, the parsing package used by tackle.  

Hook fields additionally can be marked as being rendered by default in both [python](writing-hooks.md) and [declarative hooks](declarative-hooks.md). For instance with the [`var` hook](providers/Tackle/var.md), a python hook used to render variables, the input is rendered by default so the following would work:

```yaml
stuff: things
call->: var stuff
check->: assert "{{call}}" things
```

This field can additionally be added to [declarative hooks](declarative-hooks.md#input-fields) like so:

```yaml
some_hook<-:
  input:
    default: foo
    render_by_default: true
stuff: things
schema->: some_hook --input stuff # Not things
check->: assert "{{schema.input}}" things
```

## Jinja Expressions

Jinja offers a rich expression syntax that is similar to python's and allows checking whether items are equal, items are in a list / map, and other things outside the scope of these docs that you can find in [jinja's excellent documentation](https://jinja.palletsprojects.com/en/3.0.x/templates/#expressions).

For instance to conditionally run a key based on a user input:

```yaml
user_input->: select Input what? --choices ['stuff','things']
run_stuff->: print Stuff --if user_input=='stuff'
run_things:
  ->: print Things
  if: user_input == 'things'
```

Or one could check if an item is in a list:

> Note: [`checkbox` hook](providers/Prompts/checkbox.md) is a multi-select prompt that returns a list

```yaml
user_input->: checkbox Input what? --choices ['stuff','things'] --checked
run_stuff->: print Stuff --if "'stuff' in user_input"
run_things:
  ->: print Things
  if: "'stuff' in user_input"
```

Notice in this example the extra quoting which is an artifact of yaml parsing and need to be encapsulated for the parser.

## Jinja Filters

Jinja natively has numerous builtin functions that allow a wide variety of actions similar to tackle but with less options. To see the full list, check out [jinja's documentation](https://jinja.palletsprojects.com/en/3.0.x/templates/#list-of-builtin-filters).

## List Comprehensions

While tackle supports [list comprehensions](hook-methods.md#if), jinja conveniently does as well and can be done in a single line.

```yaml
input_list:
  - stuff
  - and
  - things
reject_list:
  - and
list_comprehension->: "{{ input_list | reject('in', reject_list) | list }}"
```

Here, `reject` and `list` are builtin jinja filters, not tackle hooks.

## Calling Hooks from Jinja

Calling hooks from jinja can be convenient in a lot of situations when one wants to string hooks together. For instance here is an example using the [yaml hook](providers/Yaml/yaml.md) that reads a key from a file using a dynamic [path](providers/Paths/path_join.md) based on variable inputs.

```yaml
read_key_in_file->: "{{yaml(path_join([a_str_var,join(a_list_var),'values.yaml'])).a_key}}"
```

> Note: The above example uses a convenience macro whereby without an actual hook declaration and jinja templating, tackle interprets that as an object to rander.

Another nice pattern is to prompt a user to do something within an if statement as a one liner:

```yaml
do_thing->: do_stuff 'input' --if confirm('Do the thing?')
```
