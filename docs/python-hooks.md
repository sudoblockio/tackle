# Creating Hooks

The core business logic of tackle box is expressed in python as a collection of >100 hooks that can be easily extended with additional hooks in both python and declaratively in [yaml](declarative-hooks.md). This document covers how to create new python hooks.  For the nuances with creating importable providers, checkout the [project stucture](project-structure.md) and [creating providers](creating-providers.md) docs.

## General Overview

Python hooks are any object located within the `hooks` directory that extends a `BaseHook` object, has a `hook_name` attribute, and implements an `exec` method as the entrypoint to calling the hook. For instance given this file structure:

```
├── hooks
|  └── do_stuff.py  
└── tackle.yaml  
```

We could have a file `do_stuff.py` that has an object `DoStuffHook` that extends the `BaseHook`, has a `hook_name` attribute, and implements an `exec` method with a simple print statement like so:

#### **`do_stuff.py`**

```python
from tackle import BaseHook


class DoStuffHook(BaseHook):
    hook_name: str = "do_stuff"

    def exec(self):
        print("Doing stuff!")
```

This hook could then be called within a tackle file printing a statement.:

#### **`tackle.yaml`**
```yaml
d->: do_stuff
```

## Hook Fields

The BaseHook object is in fact a [pydantic](https://github.com/samuelcolvin/pydantic) object allowing input fields to have [types](https://pydantic-docs.helpmanual.io/usage/types/) and [validators](https://pydantic-docs.helpmanual.io/usage/validators/) which both raise useful errors if the user provides the wrong input.

For instance given the following where we added the `stuff` attribute:

```python
from tackle import BaseHook


class DoStuffHook(BaseHook):
    hook_name: str = "do_stuff"

    stuff: str = "things"

    def exec(self) -> str:
        print(f"Doing {self.stuff}!")
        return self.stuff
```

We could **optionally** override the `stuff` attribute which would be printed and returned when called as below:

```yaml
# Prints `Doing more-things`
compact->: do_stuff --stuff more-things
expanded:
  ->: do_stuff
  stuff: more-things
```

Here we can see two forms of calling a hook, the compact and expanded forms. Compact hooks have their attributes and [hook methods](hook-methods.md) accessible as flags starting with `--` whereas expanded hooks have their fields flattened out at the same level as the hook call (ie `->: do_stuff`). Both forms can be used in combination with each other.

## Hook Arguments

Hooks also have a notion of positional arguments that can be mapped to attributes when calling a hook. For instance here is an example similar to the last but with the following changes:

- No default value for the `stuff` attribute making it required
- A new `things` attribute
- An `args` field which is a list of attributes that are positionally mapped to their inputs

```python
from tackle import BaseHook


class DoStuffHook(BaseHook):
    hook_name: str = "do_stuff"
    stuff: str
    things: list = ['foo']

    # Mapper for positional arguments
    args: list = ['stuff', 'things']

    def exec(self) -> list:
        print(f"Doing {self.stuff}!")
        return self.things
```

Which could then be called as:

```yaml
compact->: do_stuff foo ['bar','baz']
expanded:
  ->: do_stuff foo
  things:
    - bar
    - baz
```

Which allows for simple compact expressions with both positional arguments and expanded forms returning the following:

```yaml
compact:
  - bar
  - baz
expanded:
  - bar
  - baz
```

> Note: Positional arguments sometimes need quoting to make sure the lexer is able to group inputs together properly.

## Hook Keyword Args

In some cases, it is useful to have additional keyword args mapped to a specific variable. For instance with the [tackle hook](https://github.com/robcxyz/tackle/blob/main/tackle/providers/tackle/hooks/tackle.py) which wraps the tackle main call, the field, `kwargs: str = "extra_context"` allows additional ,

## Hooks in Jinja

Hooks with can also be called as [jinja filters](jinja.md#jinja-filters) allowing them to be called in 2 additional ways. Jinja filters can be called with positional arguments as described in the previous section (ie `{{jinja_filter(arg1,arg2)}}`) or if they have a single positional input, with a pipe (ie `{{some_var | jinja_filter}}`). For instance the previous example could have been additionally called the following way:

```yaml
# Jinja's extension syntax with parenthesis
jinja_extension->: "{{ do_stuff('bar') }}"
# Note - piped filters need a variable as an input
foo: bar
jinja_filter->: "{{ foo | print }}"  
```

## Concepts

### Pydantic and Types

Pydantic has some idioms to be aware of when writing hooks specifically around types and fields. Every attribute needs to be declared with a type in pydantic and will throw an error if the type is not explicitly declared within the attribute's definition or if the wrong type is fed into the field. Because everything that is output from a hook needs to serializable (i.e. it can't return python objects), many [pydantic types](https://pydantic-docs.helpmanual.io/usage/types/) aren't usable unless they can be directly serialized back into a structured data format (i.e. a string, int, float, list, or dict).  

Multiple types for attributes are allowed by use of the `Union` or `Optional` types ([see difference](https://stackoverflow.com/a/51710151/15781389)) so that within the exec statement one can qualify the type and process it appropriately. For instance:

```python
from tackle import BaseHook
from typing import Union


class DoStuffHook(BaseHook):
    hook_name: str = "do_stuff"
    things: Union[str] = None
    args: list = ['things']

    def exec(self):
        if isinstance(self.things, list):
            for i in self.things:
                print(f"Thing = {i}")
        elif isinstance(self.things, str):
            print(self.things)
        return self.things
```

##### Arguments with list and dict types

Input arguments can be of any type though in practical terms, the only way to input list/map types is through rendering variable inputs. For instance given this hook:

```python
class DoStuffHook(BaseHook):
    hook_name: str = "do_stuff"
    things: dict = None
    more_things: list = None
    args: list = ['things', 'more_things']

    def exec(self):
        ...
```

One could use input args per the following tackle file:

```yaml
a_map:
  stuff: things
a_list:
  - stuff
  - things
with_rendering->: do_stuff "{{ a_map }}" "{{ a_list }}"
```

But that's a little verbose so instead we can render inputs by default as explained in the next section.

### Controlling Rendering of Fields

Sometimes it only makes sense to have inputs be maps or lists so for convenience sake there is a parameter to render strings by default so that users don't need to wrap with braces. For instance in this hook:

```python
from tackle import BaseHook, Field


class DoStuffHook(BaseHook):
    hook_name: str = "do_stuff"
    things: dict = Field(None, render_by_default=True)
```

You can see the extra Field function which when passing `render_by_default` into it, the string is automatically wrapped with jinja braces and rendered. On top of setting this on a per field basis, one could specify a list of fields like so:

```python
from tackle import BaseHook


class DoStuffHook(BaseHook):
    hook_name: str = "do_stuff"
    things: dict = None

    _render_by_default: list = ['things']
```

Which when ran in a tackle file would be:

```yaml
a_map:
  stuff: things

do-1:
  ->: do_stuff a_map  # Cleaner
do-2:
  ->: do_stuff "{{ a_map }}"  # Braces needed without render_by_default
# Validates both are equivalent
test->: assert "{{ do-1 }}" "{{ do-2 }}"
```

### Validators and `__init__`

While not a tackle specific functionality, pydantic validators and `__init__` special methods are supported.

```python
from pydantic import validator
from tackle import BaseHook


class DoStuffHook(BaseHook):
    hook_name: str = "a_hook"
    stuff: str
    args: list = ['things']

    @validator('stuff')
    def validate(cls, value):
        # Check if the input is valid - throw error otherwise
        if value == 'not-things':
            raise Exception
        return value

    def exec(self):
        return self.stuff
```

Which if called with:

```yaml
do->: do_stuff not-things
```

Would throw an exception.

### Autogenerated Documentation

Documentation can be autogenerated for hooks and providers that looks the same as the official documentation. There are two areas where documentation happens within a hook, in the docstring and within fields themselves.

```python
from tackle import BaseHook, Field


class DoStuffHook(BaseHook):
    """Put your hooks description here. Will be rendered as markdown."""
    hook_name: str = "do_stuff"
    things: dict = Field(None, description="Put the field's description here.")

    _render_by_default: list = ['things']
```

More specifics on autogenerated docs can be found in the [creating providers](creating-providers.md#autogenerated-docs) docs.
