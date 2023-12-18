from typing import TYPE_CHECKING, Optional, Union

from tackle.factory import new_context
from tackle.parser import parse_context
from tackle.utils.paths import work_in

if TYPE_CHECKING:
    from tackle.context import Context, Data, Hooks, Paths
    from tackle.types import DocumentValueType


def tackle(
    # Inputs
    *args: 'DocumentValueType',
    # Source
    checkout: Optional[str] = None,
    latest: Optional[bool] = None,
    directory: Optional[str] = None,
    file: Optional[str] = None,
    find_in_parent: bool | None = None,
    # Data
    raw_input: dict | list | None = None,
    existing_data: str | dict | None = None,
    overrides: str | dict | None = None,
    # Imports
    hooks_dir: str | None = None,
    # Context
    no_input: bool | None = None,
    verbose: bool | None = None,
    # Call
    return_context: bool | None = None,
    # Models ->
    # Used when calling tackle from tackle
    _paths: 'Paths' = None,
    _hooks: 'Hooks' = None,
    _data: 'Data' = None,
    # Unknown args/kwargs preserved for parsing
    **kwargs: 'DocumentValueType',
) -> Union['Context', 'DocumentValueType']:
    """
    Run tackle programmatically, similar to its usage from the command line. This function
    supports internal parameters like _paths, _hooks, and _data for nested tackle calls.

    Args:
        args (tuple): Variadic arguments used as the source or additional arguments for
            parsing a provider.
        checkout (str, optional): Branch, tag, or commit ID for checkout with remote providers.
        latest (bool, optional): If true, uses the latest changes from a remote tackle provider.
        directory (str, optional): Working directory relative to the base directory from `args`.
        file (str, optional): Specific file to parse, useful with remote tackle providers.
        find_in_parent (bool, optional): If true, searches for tackle files in parent directories.
        raw_input (Union[dict, list], optional): Data to parse, can be a dict or list.
        overrides (Union[str, dict], optional): Path to a file or a dict for override values.
        existing_data (Union[str, dict], optional): Reference to an unstructured file or a dict for input rendering.
        hooks_dir (str, optional): Path to the hooks directory for import.
        no_input (bool, optional): Suppresses interactive prompts, using default values.
        verbose (bool, optional): Enables verbose operation, including debug information.
        return_context (bool, optional): If true, returns the entire context; otherwise, returns public data.
        _paths (Paths, optional): Custom `Paths` object for internal use.
        _hooks (Type[BaseModel], optional): Custom hooks object for internal use.
        _data (Data, optional): Custom data object for internal use.
        kwargs (dict): Additional keyword arguments for extended functionality.

    Returns:
        Union[Context, DocumentValueType]: The context object if `return_context` is true; otherwise, returns
        the public data extracted or processed by the function.
    """
    context = new_context(
        *args,
        checkout=checkout,
        latest=latest,
        directory=directory,
        file=file,
        find_in_parent=find_in_parent,
        raw_input=raw_input,
        overrides=overrides,
        existing_data=existing_data,
        hooks_dir=hooks_dir,
        no_input=no_input,
        verbose=verbose,
        _path=_paths,
        _hooks=_hooks,
        _data=_data,
        **kwargs,
    )

    # We always change directory into the source that is being called. Needs to be this
    # or would be very confusing if writing a provider to always refer to its own path.
    with work_in(context.source.directory):
        # Main parsing logic
        parse_context(context)

    # When calling as a function, usually we just care about the public context but
    # sometimes like when calling from command line, we need to know more information
    # such as the source file format to know how to format the return of the public
    # data. See return of main in cli.py
    if return_context:
        return context
    return context.data.public
