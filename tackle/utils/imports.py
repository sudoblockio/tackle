from typing import Type, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import BaseHook, Context
    from tackle.hooks import LazyBaseFunction


def get_public_or_private_hook(
    context: 'Context',
    hook_type: str,
) -> Union[Type['BaseHook'], 'LazyBaseFunction']:
    """Get the public or private hook from the context."""
    h = context.public_hooks.get(hook_type, None)
    if h is not None:
        return h
    return context.private_hooks.get(hook_type, None)
