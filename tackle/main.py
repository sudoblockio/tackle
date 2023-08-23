from typing import TYPE_CHECKING, Union, Optional

from tackle.parser import parse_context
from tackle.contexts import new_context
from tackle.utils.paths import work_in

if TYPE_CHECKING:
    from tackle.models import Paths, Data, Hooks, Context
    from tackle.types import DocumentValueType, DocumentType

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
        input: dict | list | None = None,
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
        _paths: Optional['Paths'] = None,
        _hooks: Optional['Hooks'] = None,
        _data: Optional['Data'] = None,
        # Unknown args/kwargs preserved for parsing
        **kwargs: dict,
) -> Union['Context', 'DocumentValueType']:
    """
    Run tackle programmatically similar to how you would from a command line. Includes
     some internal params such as _paths, _hooks, and _data for calling tackle from
     tackle.

    Args:
        args (tuple): A variadic number of args used as the source or additional
            arguments when parsing a provider.
        checkout (str, optional): The branch, tag or commit ID to checkout when using
            remote providers.
        latest (bool, optional): Use the latest changes of a remote tackle provider
            instead of just the latest released tag.
        directory (str, optional): A directory to use as the working director relative
            to the base directory determined by the `args` input.
        file (str, optional): A file to parse different from a default tackle file.
            Only helpful when calling remote tackle providers.
        find_in_parent (bool, optional): Flag to make tackle search for tackle files
            in the parent directory.
        input (Union[dict, list])
        overrides (Union[str, dict], optional): A string path to a file with override
            values or a dict to use as overrides.
        hooks_dir (str, optional): Path to hooks directory to import.
        no_input (bool, optional): A flag to suppress any interactive prompts and use
            their default values.
        verbose (bool, optional): Verbose operation which includes debug info.
        return_context (bool, optional): Flag to indicate to return the whole context.
            By default, only return the public data as convenience.
        _paths (Paths, optional): A `Paths` object to use instead of
            creating one. Used when calling tackle from tackle.
        _hooks (Type[BaseModel], optional): Internal usage - a `Paths` object to use
            instead of creating one. Used when calling tackle from tackle.
        _data (Data, optional): A brief description of `_data`.
        kwargs (dict): A brief description of `kwargs`.

    Returns:
        Union[dict, list]: A brief description of the return value.
    """
    context = new_context(
        *args,
        checkout=checkout,
        latest=latest,
        directory=directory,
        file=file,
        find_in_parent=find_in_parent,
        input=input,
        overrides=overrides,
        hooks_dir=hooks_dir,
        no_input=no_input,
        verbose=verbose,
        _path=_paths,
        _hooks=_hooks,
        _data=_data,
        **kwargs
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
