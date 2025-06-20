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
