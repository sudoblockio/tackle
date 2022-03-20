
# Creating Hooks

This document covers all aspects of writing hooks in python focusing on the API and it's semantics for how it can be used within tackle files. For creating providers and creating dependencies, please check out the [creating providers](creating-providers.md) section.

## Overview

Tackle box hooks are any object located within the `hooks` directory that extends a BaseHook object and implement an `execute` method as the entrypoint to calling the hook. BaseHook objects are [pydantic](https://github.com/samuelcolvin/pydantic) objects as well such that their attributes need to include type annotations. All of these attributes are then made accessible when calling the hook from a yaml file.

There are couple other semantics that will be described in this document such as mapping arguments, excluding from rendering, and auto-generating documentation for your hooks.

## Basic Example

The easiest way to understand this is through a simple example.

If we had a file structure like this:

```
├── hooks
   └── do_stuff.py  # Name of file doesn't matter
└── tackle.yaml  # Not needed
```

We could have a file `do_stuff.py` that has an object `DoStuffHook` that extends the `BaseHook` and implements an `execute` method which in this case both prints and returns the `things` attribute. Additionally, there is a private `_args` attribute which can be used to map positional arguments to an attribute, in this case `things` (more on this later).

```python
from tackle import BaseHook, Field

class DoStuffHook(BaseHook):
    hook_type: str = "do-stuff"
    things: str = Field(None, description="All the things.")
    _args: list = ['things']

    def exec(self):
        print(self.things)
        return self.things
```

One could then run a tackle file that looks like this:

```yaml
compact-expression->: do-stuff All the things
expanded-expression:
  ->: do-stuff
  things: All the things
```

Which when run would print out "All the things" twice and return the following context.

```yaml
compact-expression: All the things
expanded-expression: All the things
```

## Concepts

### Pydantic and Types

Pydantic has some idioms to be aware of when writing hooks specifically around types and fields. Every attribute needs to be declared with a type in pydantic and will throw an error if the type is not explicitly declared within the attribute's definition or if the wrong type is fed into the field. Because everything that is output from a hook needs to serializable (i.e. it can't return python objects), many [pydantic types](https://pydantic-docs.helpmanual.io/usage/types/) aren't usable unless they can be directly serialized back into a structured data format (i.e. a string, int, float, list, or dict).  

Multiple types for attributes are allowed by use of the `Union` or `Optional` types ([see difference](https://stackoverflow.com/a/51710151/15781389)) so that within the execute statement one can qualify the type and process it appropriately. For instance:

```python
from tackle import BaseHook
from typing import Union

class DoStuffHook(BaseHook):
    hook_type: str = "do-stuff"
    things: Union[str] = None
    _args: list = ['things']

    def exec(self):
        if isinstance(self.things, list):
            for i in self.things:
                print(f"Thing = {i}")
        elif isinstance(self.things, str):
            print(self.things)
        return self.things
```

### Arguments

As you may have noticed, tackle-box supports two general types of hook calls, compact and expanded. The only way compact expressions are able to take arguments is through mapping those arguments to fields within hooks.  This is done by making an `_args` private attribute which is a list of strings pointing to the attributes the indexed arguments relate to.  For instance from our example before:

```python
class DoStuffHook(BaseHook):
    hook_type: str = "do-stuff"
    things: str = None
    more_things: str = None
    _args: list = ['things', 'more_things']
```

Now we are adding a field `more_things` which is another string that one could call like:

```yaml
compact-expression->: do-stuff All the things
```

Would be the equivalent of:

```yaml
expanded-expression:
  ->: do-stuff
  things: All
  more_things: the things
```

This is because the first argument "All" after the hook type "do-stuff" is not encapsulated with quotes and so arguments after it are grouped together. If we wanted to call it with two distinct attributes, we'd need to put quotes around them like this:

```yaml
compact-expression->: do-stuff "All the things" "with other stuff"
```

Would be the equivalent of:

```yaml
expanded-expression:
  ->: do-stuff
  things: All the things
  more_things: with other stuff
```

##### Arguments with list and dict types

Input arguments can be of any type though in practical terms, the only way to input list/map types is through rendering variable inputs. For instance given this hook:

```python
class DoStuffHook(BaseHook):
    hook_type: str = "do-stuff"
    things: dict = None
    more_things: list = None
    _args: list = ['things', 'more_things']
```

One could use input args per the following tackle file:

```yaml
a_map:
  stuff: things
a_list:
  - stuff
  - things
do->: do-stuff "{{ a_map }}" "{{ a_list }}"
```

### Controlling Rendering of Fields

Sometimes it only makes sense to have inputs be maps or lists so for convenience sake there is a parameter to render strings by default so that users don't need to wrap with braces. For instance in this hook:

```python
from tackle import BaseHook, Field

class DoStuffHook(BaseHook):
    hook_type: str = "do-stuff"
    things: dict = Field(None, render_by_default=True)
```

You can see the extra Field function which when passing `render_by_default` into it, the string is automatically wrapped with jinja braces and rendered. On top of setting this on a per field basis, one could specify a list of fields like so:

```python
from tackle import BaseHook

class DoStuffHook(BaseHook):
    hook_type: str = "do-stuff"
    things: dict = None

    _render_by_default: list = ['things']
```

Which when ran in a tackle file would be:

```yaml
a_map:
  stuff: things

do-1:
  ->: do-stuff a_map
do-2:
  ->: do-stuff "{{ a_map }}"
# Validates both are equivalent
test->: assert "{{ do-1 }}" "{{ do-2 }}"
```

### Validators and `__init__`

While not a tackle specific functionality, pydantic validators and `__init__` special methods are supported.

```python
from pydantic import validator
from tackle import BaseHook

class DoStuffHook(BaseHook):
    hook_type: str = "a_hook"
    things: dict = None
    more_things: list = None
    _args: list = ['things', 'more_things']

    @validator('things')
    def validate(cls, value):
        # Check if the input is valid - throw error otherwise
        ...
        return value

    def __init__(self, **data):
        super().__init__(**data)
        # Initialize the object
        ...

    def exec(self):
        ...
```

### Autogenerated Documentation

Documentation can be autogenerated for hooks and providers that looks the same as the official documentation. There are two areas where documentation happens within a hook, in the docstring and within fields themselves.

```python
from tackle import BaseHook, Field

class DoStuffHook(BaseHook):
    """Put your hooks description here. Will be rendered as markdown."""
    hook_type: str = "do-stuff"
    things: dict = Field(None, description="Put the field's description here.")

    _render_by_default: list = ['things']
```

More specifics on autogenerated docs can be found in the [creating providers](creating-providers.md#autogenerated-docs) docs.
