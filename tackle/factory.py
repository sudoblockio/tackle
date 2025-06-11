"""
TODO: This is old awful code... Please don't look...
"""
from __future__ import annotations

import os
from copy import copy
from pathlib import Path
from typing import Optional, Union

from ruyaml.parser import ParserError

from tackle import exceptions
from tackle.context import Context, Data, Hooks, InputArguments, Paths, Source
from tackle.imports import (
    import_hooks_from_hooks_directory,
    import_native_providers,
    import_with_fallback_install,
)
from tackle.settings import settings
from tackle.utils.files import read_config_file
from tackle.utils.paths import (
    find_hooks_dir_from_tests,
    find_hooks_directory_in_dir,
    find_tackle_base_in_parent_dir,
    find_tackle_base_in_parent_dir_with_exception,
    find_tackle_file_in_dir,
    is_directory_with_tackle,
    is_file,
    is_repo_url,
)
from tackle.utils.vcs import get_repo_source
from tackle.utils.zipfiles import unzip


def format_path_to_name(path: str) -> str:
    return os.path.basename(os.path.split(path)[0]).replace('-', '_').replace(' ', '_')


def create_hooks(
    context: 'Context',
    hooks_dir: str = None,
    _hooks: 'Hooks' = None,
):
    """
    Create the hooks object which has three namespaces, native, public, and private.
     Native hooks are instantiated once and are passed between tackle calls / contexts.
     Public and private hooks are local to a tackle context and are not passed between
     one another.
    """
    # Check if tackle hooks (_hooks) are passed
    if _hooks is None and context.hooks is None:
        context.hooks = Hooks()
    elif context.hooks is None and _hooks is not None:
        # Otherwise we have hooks passed in and only need to carry over the native hooks
        context.hooks = _hooks
    else:
        raise Exception("Should never happen...")

    # We should clear public / private hooks here now that native hooks are separated
    if context.hooks.public is None:
        context.hooks.public = {}

    if context.hooks.private is None:
        context.hooks.private = {}

    # These should be the only things carried over between contexts
    if context.hooks.native is None:
        # Initialize the native providers / hooks
        context.hooks.native = {}
        context.hooks.native = import_native_providers()

    if hooks_dir is not None:
        # Provided by command line arg
        import_hooks_from_hooks_directory(
            context=context,
            provider_name=format_path_to_name(path=hooks_dir),
            hooks_directory=hooks_dir,
        )
    if context.source.hooks_dir is not None:
        # Detected from source if there is a hooks directory at the base
        import_with_fallback_install(
            context=context,
            provider_name=context.source.name,
            hooks_directory=context.source.hooks_dir,
        )


def extract_base_file(context: 'Context') -> list | dict:
    """Read the tackle file and initialize input_context."""
    if context.source.file:
        try:
            raw_input = read_config_file(context.source.file)
        except ParserError as e:
            raise exceptions.TackleFileInitialParsingException(e) from None  # noqa
        if raw_input is None:
            raise exceptions.EmptyTackleFileException(
                f"Tackle file found at {os.path.join(context.source.directory)} is empty.",
                context=context,
            ) from None
    else:
        raw_input = {}
    return raw_input


def get_overrides(
    context: 'Context',
    data: Optional['Data'],
    overrides: Union[str, dict],
):
    """
    Overrides can be string references to files or a dict, both of which are used to
     override values that would be parsed into the public data.
    """
    if overrides is None:
        return
    elif isinstance(overrides, str):
        if os.path.exists(overrides):
            override_dict = read_config_file(overrides)
            if override_dict is not None:
                data.overrides.update(override_dict)
                # context.input.kwargs.update(override_dict)
        else:
            raise exceptions.UnknownSourceException(
                f"The `override` input={overrides}, when given as a string must "
                f"be a path to an file. Exiting.",
                context=context,
            )
    elif isinstance(overrides, dict):
        data.overrides.update(overrides)
        # context.input.kwargs.update(overrides)


def new_data(
    *,
    context: 'Context',
    raw_input: dict | list | None = None,
    overrides: str | dict | None = None,
    existing_data: str | dict | None = None,
    _data: Data | None = None,
) -> Data:
    """
    Create a data object which stores data as the source is parsed. When tackle is
     called between contexts (ie different sources / within a tackle file in blocks),
     data needs to be transferred from public to existing.

    See memory management docs for more details on the various namespaces for data.
    https://sudoblockio.github.io/tackle/memory-management/
    """
    # Data can be passed from one tackle call to another
    if _data is None:
        if context.data is None:
            data = Data()  # New data
        else:
            # This is a hack where we can take dict / list args in the main tackle
            # function and to bypass the source logic, we simply create the data object
            # with the raw data which is the only way context can have data here.
            data = context.data
    else:
        # Data has been passed
        data = _data

    if existing_data is None:
        existing_data = {}
    elif isinstance(existing_data, str):
        # We have a reference to a file
        existing_data = read_config_file(existing_data)
    elif not isinstance(existing_data, dict):
        raise exceptions.UnknownHookInputArgumentException(
            "A non-string reference to a file or non-dict value for `existing_data` "
            "argument was supplied. Exiting...",
            context=context,
        )

    if data.existing is None:
        data.existing = {}

    if data.overrides is None:
        data.overrides = {}

    if data.public is not None:
        # If we were passed a data object by calling tackle from tackle then the
        # parent's public data is used as existing which is immutable
        if _data is not None and isinstance(_data.public, dict):
            data.existing.update(_data.public)
        else:
            data.existing = {}

        # Wipe the public data as we don't know the type yet -> ie list or dict
        data.public = None
        data.private = None

    get_overrides(context=context, data=data, overrides=overrides)

    if raw_input is None:
        data.raw_input = extract_base_file(context=context)
    else:
        data.raw_input = raw_input

    if isinstance(data.raw_input, list):
        # Change output to empty list
        data.public = []
        data.private = []
    else:
        data.public = {}
        data.private = {}

    if data.existing is None:
        data.existing = {}

    # Finally update the existing data
    data.existing.update(existing_data)

    data.hooks_input = {}  # Container for any declarative hooks
    if isinstance(data.raw_input, dict):
        data.pre_input = {}
        data.post_input = {}
    elif isinstance(data.raw_input, list):
        # List inputs won't be helpful in the pre input data so ignoring
        data.pre_input = []
        data.post_input = data.raw_input
        # Dcl hooks can only be defined in objects, not lists unless there is some
        # good reason to support that. Nothing else to do here
    else:
        raise Exception("This should never happen since it is caught in parsing error.")

    return data


def new_path(
    *,
    context: 'Context',
    _path: Optional[Paths],
) -> Paths:
    """
    Create `Paths` object which stores the paths that are being parsed. Divided into
     three sections:
    - calling: The original path that called tackle. Since tackle calls can be embedded,
    this path won't change regardless of how many times tackle was called.
    - current: The path currently being parsed. If this is a remotely imported tackle
    provider, this will be the path that called the tackle provider, not the path of
    the remote provider.
    - tackle: The path to the tackle provider being parsed which if it is a remote
    tackle provider, will be in the XDG config directory (ie on linux
    ~./.config/tackle/providers/<provider_name>).
    """
    if _path is not None:
        return Paths(
            current=context.source,
            calling=_path.current,
            tackle=context.source,
        )
    else:
        # TODO: Fix logic for tackle or RM
        return Paths(
            current=context.source,
            calling=context.source,
            tackle=context.source,
        )


def update_source(
    context: 'Context',
    source: Source,
    directory: str,
    file: str,
):
    """
    Once we have identified a tackle base, we then need to check if the `directory` or
     `file` inputs to see if the call actually relates to a dir/file within that tackle
     base. This is needed especially in the context of remote providers where we could
     be trying to call a tackle file within a sub directory of that source.
    """
    # `directory` is a command line argument that is used as the working directory when
    # parsing a provider. It is usually the same as `source.base` unless it is specified
    # as an argument. The two are different as we need a way to tell the difference
    # between the base of a provider where a hooks directory is imported and a
    # directory within a provider that could contain tackle files to be parsed.
    if directory is not None:
        directory_path = os.path.join(source.base_dir, directory)
        if not os.path.isdir(directory_path):
            raise exceptions.UnknownSourceException(
                f"Unknown directory={directory_path} within the tackle provider"
                f" {source.base_dir}. Exiting...",
                context=context,
            ) from None
        source.directory = directory_path
    else:
        source.directory = source.base_dir

    # `file` is a command line argument that is used to parse non-tackle files within a
    # provider. It is normally populated by detecting a tackle file unless specified.
    if file is not None:
        file_path = os.path.join(source.directory, file)
        if not os.path.isfile(file_path):
            raise exceptions.UnknownSourceException(
                f"Unknown file={file_path} within the tackle provider"
                f" {source.base_dir}. Exiting...",
                context=context,
            ) from None
        source.file = file_path
    elif source.file is None:
        file = find_tackle_file_in_dir(directory=source.directory)
        if file is None:
            file = find_tackle_file_in_dir(directory=source.base_dir)
        source.file = file

    source.hooks_dir = find_hooks_directory_in_dir(directory=source.base_dir)


def new_source_from_unknown_args(
    context: 'Context',
    source: Source,
    first_arg: str,
    directory: str = None,
    file: str = None,
) -> Source:
    """
    Tackle has been called without an arg that could be recognized as a source so we
     need to check if there is a tackle file in the current or parent directory and if
     there is, use that as source and don't consume the arg. Will raise error later if
     the arg was not used.
    """
    source.base_dir = find_tackle_base_in_parent_dir(directory=os.path.abspath('.'))
    if source.base_dir is None:
        raise exceptions.UnknownSourceException(
            f"No tackle source or base directory was found with the "
            f"argument=`{first_arg}`. Exiting...",
            context=context,
        ) from None
    # Reinsert the arg back into the args
    context.input.args.insert(0, first_arg)
    source.name = format_path_to_name(path=source.base_dir)
    update_source(
        context=context,
        source=source,
        directory=directory,
        file=file,
    )
    return source


def new_source(
    context: 'Context',
    checkout: str = None,
    latest: bool = None,
    directory: str = None,
    file: str = None,
    find_in_parent: bool = None,
    _strict_source: bool = False,
    _source: Source = None,
) -> Source:
    """
    Create a `source` object by extracting the first argument given to tackle and then
     using that to determine the source. Works with the following logic:
    - If no arg is given, find the source in the parent directory
    - If `find_in_parent` is given, search in the parent dir for tackle base
    - If the arg is a list or dict, then use that as a raw input to be parsed
    - If the arg is not a string, list, or dict, find a tackle base and reinsert the arg
    - If the arg is a zip file and exists, use that
    - If the arg is a json, yaml, toml file, parse that
    - If the arg is to a dir with a tackle base, use that
    - If the arg looks like a remote provider (ie str/str or https://github*), use that
    """
    if _source is not None:
        # Skip importing a source if it already there (ie we are creating temp context)
        return _source
    source = Source(calling_directory=os.path.abspath('.'))
    if len(context.input.args) > 0:
        first_arg = context.input.args.pop(0)
        # `find_in_parent` is a command line argument that tries to find a base
        # directory in the parent. It does not include the current directory in search
        if find_in_parent:
            source.find_in_parent = True
            source.base_dir = find_tackle_base_in_parent_dir_with_exception(
                context=context,
                directory=os.path.abspath('..'),
            )
            source.name = os.path.basename(source.base_dir)
            update_source(
                context=context,
                source=source,
                directory=directory,
                file=file,
            )
            source.hooks_dir = find_hooks_directory_in_dir(directory=source.base_dir)
            context.input.args.insert(0, first_arg)
        elif isinstance(first_arg, (dict, list)):
            # Will be picked up later in data as the input_raw to be parsed
            source.raw = first_arg
        elif not isinstance(first_arg, str):
            # We didn't recognize a non-string arg so we fallback on looking in parent
            # directory and reinsert the arg into the context.input.args. Need this
            # condition here as all other source detection depends on the first_arg
            # being a string.
            source = new_source_from_unknown_args(
                context=context,
                source=source,
                first_arg=first_arg,
                directory=directory,
                file=file,
            )
        # Zipfile
        elif first_arg.lower().endswith('.zip') and os.path.isfile(first_arg):
            source.base_dir = unzip(
                zip_uri=first_arg,
                clone_to_dir=settings.tackle_dir,
                no_input=context.no_input,
                # password=password,  # TODO: RM - Should prompt?
            )
            source.name = format_path_to_name(path=first_arg)
            update_source(
                context=context,
                source=source,
                directory=directory,
                file=file,
            )
            source.hooks_dir = find_hooks_directory_in_dir(directory=source.base_dir)
        # Repo
        elif is_repo_url(first_arg):
            if latest:
                if checkout is not None:
                    raise exceptions.UnknownSourceException(
                        "Can't specify `checkout` and `latest` flags at the same time.",
                        context=context,
                    )
            source.base_dir = get_repo_source(
                repo=first_arg,
                version=checkout,
                latest=latest,
            )
            source.name = first_arg.replace('/', '_')
            update_source(
                context=context,
                source=source,
                directory=directory,
                file=file,
            )
            source.hooks_dir = find_hooks_directory_in_dir(directory=source.base_dir)
        # Directory
        elif is_directory_with_tackle(first_arg):
            # Special case where the input is a path to a directory with a provider
            source.base_dir = os.path.abspath(first_arg)
            source.name = format_path_to_name(path=source.base_dir)
            update_source(
                context=context,
                source=source,
                directory=directory,
                file=file,
            )
        # File
        elif file is None and is_file(first_arg, directory):
            if directory is not None:
                file_path = os.path.join(directory, first_arg)
            else:
                file_path = os.path.abspath(first_arg)
            source.file = file_path
            source.directory = source.base_dir = str(Path(file_path).parent.absolute())
            source.name = format_path_to_name(path=source.base_dir)
            source.hooks_dir = find_hooks_directory_in_dir(
                directory=str(source.base_dir)
            )
        else:
            if _strict_source:
                raise exceptions.UnknownSourceException(
                    f"The source=`{first_arg}` was not recognized. Exiting...",
                    context=context,
                )
            # We didn't recognize a string arg so we fallback on looking in parent
            # directory and reinsert the arg into the context.input.args
            source = new_source_from_unknown_args(
                context=context,
                source=source,
                first_arg=first_arg,
                directory=directory,
                file=file,
            )
    else:
        # We weren't given an arg, so we need to look for a tackle base in the current
        # or parent directories.
        source.base_dir = find_tackle_base_in_parent_dir_with_exception(
            context=context,
            directory=os.path.abspath('.'),
        )
        source.name = format_path_to_name(path=source.base_dir)
        update_source(
            context=context,
            source=source,
            directory=directory,
            file=file,
        )
        source.find_in_parent = True
    if source.hooks_dir is None and source.base_dir is not None:
        source.hooks_dir = find_hooks_dir_from_tests(source.base_dir)

    return source


def new_inputs(
    args: tuple = None,
    kwargs: dict = None,
) -> InputArguments:
    """
    Create a `input` object which holds the args/kwargs to create a source and then
     get consumed by the parser.
    """
    if args == (None,):
        # Happens when there is no input to the commandline
        args = []
    else:
        # Happens when we use tackle as package
        args = list(args)

    if kwargs is None:
        kwargs = dict()

    input_obj = InputArguments(
        args=args,
        kwargs=kwargs,
        # string is for printing out the help screen as the vars are mutable above, and
        # so we need to preserve here. Trimming last arg which should be `help`
        help_string=f"{' '.join(args[:-1])} {' '.join([f'--{k} {v}' for k, v in kwargs.items()])}",
    )

    return input_obj


def new_context(
    # Inputs
    *args: Union[str, dict, list],
    # Source
    checkout: str = None,
    latest: bool = None,
    directory: str = None,
    file: str = None,
    find_in_parent: bool = None,
    hooks_dir: str = None,
    _strict_source: bool = False,  # Raise if source not found
    # Data
    raw_input: dict | list | None = None,
    overrides: Union[str, dict] = None,
    existing_data: str | dict | None = None,
    # Context
    no_input: bool = None,
    verbose: bool = None,
    # Models -> Used when calling tackle from tackle
    _path: 'Paths' = None,
    _hooks: 'Hooks' = None,
    _data: 'Data' = None,
    _source: 'Source' = None,
    # Unknown args/kwargs preserved for parsing
    **kwargs: dict,
) -> 'Context':
    """Create a new context. See tackle.main.tackle for options which wraps this."""
    context = Context(
        no_input=no_input if no_input is not None else False,
        verbose=verbose if verbose is not None else False,
        key_path=[],
        key_path_block=[],
    )
    context.input = new_inputs(
        args=args,
        kwargs=kwargs,
    )
    context.source = new_source(
        context=context,
        checkout=checkout,
        latest=latest,
        directory=directory,
        file=file,
        find_in_parent=find_in_parent,
        _strict_source=_strict_source,
        _source=_source,
    )
    context.path = new_path(
        context=context,
        _path=_path,
    )
    context.data = new_data(
        context=context,
        raw_input=raw_input,
        overrides=overrides,
        existing_data=existing_data,
        _data=_data,
    )
    create_hooks(
        context=context,
        hooks_dir=hooks_dir,
        _hooks=_hooks,
    )

    return context


def new_context_from_context(context: Context, **kwargs):
    """
    Create a new context from an existing context that carries over essential
     information such as
    """
    return new_context(
        no_input=context.no_input,
        verbose=context.verbose,
        _path=context.path,
        # _hooks=context.hooks,
        **kwargs,
    )
