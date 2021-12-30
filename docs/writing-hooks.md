
# Creating Hooks

This document covers all aspects of writing hooks focusing on the API and it's semantics for how it can be used within tackle files. For creating providers and creating dependencies, please check out the [creating providers](creating-providers.md) section.

## Overview

Tackle box hooks are any object located within the `hooks` directory that extends a BaseHook object and implement an `execute` method as the entrypoint to calling the hook. BaseHook objects are [pydantic](https://github.com/samuelcolvin/pydantic) objects as well such that their attributes need to include type annotations. All of these attributes are then made accessible when calling the hook from a yaml file.

There are couple other semantics that will be described in this document such as mapping arguments, excluding from rendering, and auto-generating documentation for your hooks that will be covered later in this document.

## Basic Example

The easiest way to understand this is through a simple example.

If we had a file structure like this:

```
├── hooks
   └── do_stuff.py  # Name of file doesn't matter
└── tackle.yaml  # Not needed
```

We could have a file `do_stuff.py` that has an object `DoStuffHook` that extends the `BaseHook` and implements an `execute` method which in this case both prints and returns the `things` attribute. Additionally there is a private `_args` attribute which can be used to map positional arguments to an attribute, in this case `things` (more on this later).

```python
from tackle import BaseHook, Field

class DoStuffHook(BaseHook):
    type: str = "do-stuff"
    things: str = Field(None, description="All the things.")
    _args: list = ['things']

    def execute(self):
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

### Pydantic and Types / Fields

Pydantic has some idioms to be aware of when writing hooks specifically around types and fields. Every attribute needs to be declared with a type in pydantic and will throw an error if the type is not explicitly declared within the attribute's definition or if the wrong type is fed into the field. Because everything that is output from a hook needs to serializable (i.e. it can't return python objects), many [pydantic types](https://pydantic-docs.helpmanual.io/usage/types/) aren't usable unless they can be directly serialized back into a structured data format (i.e. a string, int, float, list, or dict).  

Multiple types for attributes are allowed by use of the `Union` or `Optional` types ([see difference](https://stackoverflow.com/a/51710151/15781389)) so that within the execute statement one can qualify the type and process it appropriately. For instance:

```python
from tackle import BaseHook, Field
from typing import Union

class DoStuffHook(BaseHook):
    type: str = "do-stuff"
    things: Union[str] = None
    _args: list = ['things']

    def execute(self):
        if isinstance(self.things, list):
            for i in self.things:
                print(f"Thing = {i}")
        elif isinstance(self.things, str):
            print(self.things)
        return self.things
```
****

- [ ] TODO
-


### Arguments

As you may have noticed, tackle-box supports two general types of hook calls, compact and expanded. The only way compact expressions are able to take arguments is through mapping those arguments to fields within hooks.  This is done by making an `_args` private attribute which is a list of strings pointing to the attributes the indexed arguments relate to.  For instance from our example before:

```python
class DoStuffHook(BaseHook):
    type: str = "do-stuff"
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

- [ ] TODO

### Controlling Rendering of Fields




> As of the time of this writing, `validator` objects are not supported but hopefully will be in the future
