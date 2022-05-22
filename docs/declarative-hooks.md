# Declarative Hooks

Declarative hooks are very similar to python hooks in that they offer a way interface with business logic from within a tackle file but instead of being written in python, they are written within tackle files themselves. They are useful when you want to create reusable logic, interface with schemas, or create CLI's with rich option sets out of tackle files. They have strongly typed input parameters and can have object-oriented properties such as inheritance and methods that can be passed between hooks.

### Basic Usage

Declarative hooks are keys that end with an arrow to the left, `<-` for public hooks / `<_` for private hooks (more on this later), which is the same as hook calls but in the opposite direction.

For instance the following shows both a declarative hook and a call of that hook.

```yaml
declarative_hook<-:
  input: str
hook_call:
  ->: declarative_hook
  input: stuff
```

Declarative hooks have no required fields as in the example above the hook is simply used to validate the input and by default will simply return the input parameters.

```yaml
hook_call:
  input: stuff
```

#### `exec` method

If you want the hook to actually do something, the hook will need to have an `exec` method similar to how a [python hooks](writing-hooks.md) have the same.  As a simple example, here we are creating a hook `greeter` that prints `Hello world!`:

```yaml
greeter<-:
  exec:
    target: world
    hi_>: print Hello {{target}}!
call->: greeter
```

By default, declarative hooks return the entire context from the exec method so in the example above, the output would be:

```yaml
call:
  target: world
```

This is because the key `hi_>` is a private hook call (see [memory management](memory-management.md) for more info) and only the public context is returned.

#### `return` key

If you want to only return a part of the exec call, the `return` key is available for this. For instance given the following example:

```yaml
greeter<-:
  exec:
    target: world
    hi->: print Hello {{target}}!
  return: target
call->: greeter
```

The output would now be:

```yaml
call: world
```

As the `return` key dereferences the `target` from the exec method.  

> TODO: Future versions will allow more flexible return inputs

#### Input fields

In each of the previous examples, the input type for the `target` field was infered by the default value but it is possible to make the input fields strongly typed just like [python hooks](writing-hooks.md). This can be done in two different ways, by giving the type as a string or as a map with named fields the same as [pydantic's `Field`](https://pydantic-docs.helpmanual.io/usage/schema/#field-customization) function.

When the types are given as literals, they are also by default required. For instance the following hook would require each of the inputs with their corresponding type.

```yaml
some_hook<-:
  a_str: str
  a_bool: bool
  a_int: int
  a_float: float
  a_list: list
  a_dict: dict
call:
  ->: some_hook
  a_str: foo
  a_bool: true
  a_int: 1
  a_float: 1.2
  a_list: ['stuff', 'things']  
  a_dict: {'stuff': 'things'}
```

Additionally, hook fields can be declared with key value pairs corresponding to [pydantic's `Field`](https://pydantic-docs.helpmanual.io/usage/schema/#field-customization) inputs. For instance the following would be able to validate the type of an `input` field of type string:

```yaml
some_hook<-:
  input:
    type: str
    default: foo
    regex: ^foo.*
pass->: some_hook --input foo-bar
fail->: some_hook --input bar
```

The type field does not need to be populated if given a default and the same type can be inferred.

```yaml
some_hook<-:
  input:
    default:
      - stuff
      - things
call:
  ->: some_hook --input foo --try
  except:
    p->: print Wrong type!!
```

#### Methods

Declarative hooks can have methods that can be called similar to how the `exec` method is called. For instance the following would print out "Hello world!".

```yaml
words<-:
  hi: Wadup
  say<-:
    target: str
    exec:
      p->: print {{hi}} {{target}}

p->: words.say --hi Hello --target world!
```

Here you can see that there is method `say` that when called executes its own `exec` method which is able to access the base attribute `hi`.  This is useful in many contexts where one wants to extend base objects with additional functionality.

> Future versions are contemplating ways to do method overloading based on types. Stay tuned.

#### Extending Hooks

Tackle has the notion of extending hooks from base hooks similar to inheritance patterns found in OOP languages. This is useful if you have a schema that you want to use in multiple hooks or you want to create generic methods that apply to multiple schemas. For instance:

```yaml
base<-:
  hi:
    default: Hello

words<-:
  extends: base
  say<-:
    target: str
    exec:
      p->: print {{hi}} {{target}}

p->: words.say --target world!
```

Here we can see some base hook `base` which is then extended in the `words` hook.

> Note: Future versions of tackle will support inheriting from common schemas like OpenAPI and have generic classes that
