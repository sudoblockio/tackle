from typing import TYPE_CHECKING

from tackle.macros.key_macros import key_macro
from tackle.macros.value_macros import value_macro

if TYPE_CHECKING:
    from tackle import Context, DocumentValueType


def run_macros(
        *,
        context: 'Context',
        value: 'DocumentValueType',
) -> 'DocumentValueType':
    """Parse out the arrow and run key then value macros if an arrow exists."""
    key = context.key_path[-1]
    ending = key[-2:]
    is_hook = ending in ('->', '_>')
    if is_hook:
        # Only act on hooks
        key = key[:-2]
        return value_macro(
            context=context,
            value=key_macro(context=context, key=key, value=value, arrow=ending),
        )
    return value
