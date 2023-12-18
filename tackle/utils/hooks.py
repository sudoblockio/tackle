from typing import Type

from tackle import BaseHook
from tackle.factory import new_context
from tackle.hooks import get_hook_from_context


def get_hook(
    hook_name: str,
    source: str = '.',
    args: list = None,
) -> Type[BaseHook]:
    """
    Retrieves and returns a hook object for testing purposes.

    This function simplifies the process of importing hooks by handling the import
     logic and returning the hook object, which can then be used for testing. It
     supports splitting the hook name to handle method calls or using arguments.
     For instance `hook_name='foo.bar'` is the same as `hook_name='foo', args=['bar']`

    Args:
        hook_name (str): The name of the hook to be retrieved. If the hook name
            contains a '.', it is split, and the part after the last '.' is treated
            as an argument.
        source (str, optional): The source path from which the hook is to be imported.
            Defaults to '.' (current directory).
        args (list, optional): A list of arguments to be passed to the hook. If not
            provided or None, an empty list is used. If `hook_name` contains a '.',
            this is overridden with the part after the last '.'.

    Returns:
        object: The hook object retrieved based on the provided `hook_name`.

    Raises:
        Exception: If the hook cannot be retrieved or an error occurs during the
            import process.
    """
    if args is None:
        args = []

    context = new_context(source)

    # Break up any hook_name with a '.' indicating a method call which is taken as arg
    hook_name_parts = hook_name.split('.')
    if len(hook_name_parts) != 1:
        args = hook_name_parts[-1:]

    Hook = get_hook_from_context(
        context=context,
        hook_name=hook_name,
        args=args,
        throw=True,
    )

    return Hook
