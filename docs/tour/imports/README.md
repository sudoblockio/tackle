# Imports with Tackle

Objects declared in tackle can be imported in python and visa versa.

```shell
#pip install tackle
python3 demo.py
```

[//]: # (--start--)


#### Dir structure 

```   
├── demo.py
├── hooks
│   ├── foo.py
│   └── foo.yaml
└── other_hooks
    └── bar.py
```

#### [demo.py](demo.py)

```python
from pydantic import ValidationError

from tackle import get_hook

# Import hooks defined in the `hooks` directory
FooModel = get_hook('FooModel')
FooHook = get_hook('FooHook')
FooExtended = get_hook('FooExtended')
BarExtended = get_hook('BarExtended')


class FooModelExtended(FooModel):
    """Can extend hooks imported from tackle files."""
    baz: int


# Valid instantiations
foo_hook = FooHook(bar=42)
foo_model = FooModel(bar=42)
foo_extended = FooExtended(bar=42, baz=42)
bar_extended = BarExtended(bar=42, baz=42)
foo_model_extended = FooModelExtended(bar=42, baz=42)


def validate_model(model, **kwargs):
    try:
        model(**kwargs)
    except ValidationError as e:
        print(e)
    else:
        raise AssertionError("Should be invalid...")


for m in [FooHook, FooModel, FooExtended, BarExtended, FooModelExtended]:
    validate_model(m, bar="not-ok")

```

#### [hooks/foo.py](hooks/foo.py)

```python
from tackle import BaseHook


class FooModel(BaseHook):
    bar: int

```

#### [hooks/foo.yaml](hooks/foo.yaml)

```yaml
import->:
  - other_hooks/bar.py

FooHook<-:
  bar:
    type: int

FooExtended<-:
  extends: FooModel
  baz: int

BarExtended<-:
  extends: BarModel
  help: Importing `other_hooks` yields a BareModel which we're going to extend here.
  baz: int

```

#### [other_hooks/bar.py](other_hooks/bar.py)

```python
from tackle import BaseHook


class BarModel(BaseHook):
    bar: int

```
[//]: # (--end--)