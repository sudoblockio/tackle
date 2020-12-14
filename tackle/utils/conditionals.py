"""Conditional utilities."""
from tackle.render import render_variable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context


def evaluate_when(hook_dict: dict, context: 'Context'):
    """Evaluate the when condition and return bool."""
    if 'when' not in hook_dict:
        return True

    when_raw = hook_dict['when']
    when_condition = False
    if isinstance(when_raw, str):
        when_condition = render_variable(context, when_raw)
    elif isinstance(when_raw, list):
        # Evaluate lists as successively evalutated 'and' conditions
        for i in when_raw:
            when_condition = render_variable(context, i)
            # If anything is false, then break immediately
            if not when_condition:
                break

    hook_dict.pop('when')

    return when_condition
