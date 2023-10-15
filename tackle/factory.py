import os
from pathlib import Path
from typing import Union, Optional
from ruyaml.parser import ParserError

from tackle import exceptions
from tackle.models import Context, Data, InputArguments, Source, Hooks, Paths
from tackle.settings import settings
from tackle.utils.paths import (
    is_repo_url,
    is_directory_with_tackle,
    is_file,
    find_tackle_file_in_dir,
    find_hooks_directory_in_dir,
    find_tackle_base_in_parent_dir,
    find_tackle_base_in_parent_dir_with_exception
)
from tackle.utils.vcs import get_repo_source
from tackle.utils.zipfile import unzip
from tackle.utils.files import read_config_file
from tackle.imports import import_native_providers, import_hooks_from_hooks_directory


def format_path_to_name(path: str) -> str:
    return os.path.basename(os.path.split(path)[0]).replace('-', '_').replace(' ', '_')


def create_hooks(
        context: 'Context',
        _hooks: Hooks = None,
        hooks_dir: str = None,
):
    if _hooks is None and context.hooks is None:
        context.hooks = Hooks()
    elif context.hooks is None and _hooks is not None:
        # Otherwise we have hooks passed in
        context.hooks = _hooks
    else:
        raise Exception("Should never happen...")

    if not context.hooks.private:
        # Initialize the native providers / hooks
        context.hooks.private = import_native_providers(context=context)

    if hooks_dir is not None:
        # Provided by command line arg
        import_hooks_from_hooks_directory(
            context=context,
            provider_name=format_path_to_name(path=hooks_dir),
            hooks_directory=hooks_dir,
        )
    if context.source.hooks_dir is not None:
        # Detected from source if there is a hooks directory at the base
        import_hooks_from_hooks_directory(
            context=context,
            provider_name=context.source.name,
            hooks_directory=context.source.hooks_dir,
        )


def extract_base_file(context: 'Context', data: 'Data'):
    """Read the tackle file and initialize input_context."""
    if context.source.file:
        try:
            data.raw_input = read_config_file(context.source.file)
        except ParserError as e:
            raise exceptions.TackleFileInitialParsingException(e) from None  # noqa
        if data.raw_input is None:
            raise exceptions.EmptyTackleFileException(
                f"Tackle file found at {os.path.join(context.source.directory)} is empty.",
                context=context
            ) from None
    else:
        data.raw_input = {}


def get_overrides(
        context: Context,
        data: Optional['Data'],
        overrides: Union[str, dict],
):
    if overrides is None:
        return
    elif isinstance(overrides, str):
        if os.path.exists(overrides):
            override_dict = read_config_file(overrides)
            if override_dict is not None:
                data.overrides.update(override_dict)
        else:
            raise exceptions.UnknownInputArgumentException(
                f"The `override` input={overrides}, when given as a string must "
                f"be a path to an file. Exiting.",
                context=context,
            )
    elif isinstance(overrides, dict):
        data.overrides.update(overrides)


def new_data(
        *,
        context: Context,
        input: dict | list | None = None,
        overrides: str | dict | None = None,
        existing_data: str | dict | None = None,
        _data: Data | None = None,
) -> Data:
    """

    """
    # Data can be passed from one tackle call to another
    if _data is None:
        if context.data is None:
            data = Data()
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
        raise exceptions.UnknownInputArgumentException(f"", context=context)

    if data.existing is None:
        data.existing = {}

    if data.overrides is None:
        data.overrides = {}

    if data.public is not None:
        # If we were passed a data object by calling tackle from tackle then the
        # parent's public data is used as existing which is immutable
        if isinstance(_data.public, dict):
            data.existing.update(_data.public)
        else:
            data.existing = {}

        # Wipe the public data as we don't know the type yet -> ie list or dict
        data.public = None
        data.private = None

    get_overrides(context=context, data=data, overrides=overrides)

    if input is None:
        extract_base_file(context=context, data=data)
    else:
        data.raw_input = input

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
    elif isinstance(context.data.raw_input, list):
        # List inputs won't be helpful in the pre input data so ignoring
        context.data.pre_input = []
        context.data.post_input = context.data.raw_input
        # Dcl hooks can only be defined in objects, not lists unless there is some
        # good reason to support that. Nothing else to do here
    else:
        raise Exception("This should never happen since it is caught in parsing error.")


    return data


def new_path(
        *,
        context: Context,
        _path: Optional[Paths],
) -> Paths:
    if _path is None:
        return Paths(
            current=context.source,
            calling=context.source,
            tackle=context.source,
        )
    else:
        # TODO: Fix logic for tackle or RM
        return Paths(
            current=context.source,
            calling=_path.current,
            tackle=context.source,
        )


def update_source(
        context: Context,
        source: Source,
        directory: str,
        file: str,
):
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
                context=context
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
                context=context
            ) from None
        source.file = os.path.basename(file_path)
    elif source.file is None:
        file = find_tackle_file_in_dir(dir=source.directory)
        if file is None:
            file = find_tackle_file_in_dir(dir=source.base_dir)
        source.file = file

    source.hooks_dir = find_hooks_directory_in_dir(dir=source.base_dir)


def new_source_from_non_string_args(
        context: Context,
        source: Source,
        first_arg: str,
        directory: str = None,
        file: str = None,
) -> Source:
    # Special case where we feed in some other type of arg
    update_source(
        context=context,
        source=source,
        directory=directory,
        file=file,
    )
    if source.directory is not None:
        source.base_dir = os.path.abspath('.')
    else:
        source.base_dir = source.directory

    if source.file is not None:
        base_directory = find_tackle_base_in_parent_dir(dir=os.path.abspath('.'))
        if isinstance(first_arg, (dict, list)):
            context.data = Data(raw_input=first_arg)
        else:
            raise exceptions.UnknownInputArgumentException(
                f"The argument={first_arg} was not recognized and no file "
            )
    context.input.args.insert(0, first_arg)

    source.name = os.path.basename(source.base_dir)

    return source


def new_source(
        context: Context,
        checkout: str = None,
        latest: bool = None,
        directory: str = None,
        file: str = None,
        find_in_parent: bool = None,
) -> Source:
    """
    - Parses args to create source object
    - Persists the providers being called if remote
    """
    source = Source()
    if len(context.input.args) > 0:
        first_arg = context.input.args.pop(0)
        # `find_in_parent` is a command line argument that tries to find a base
        # directory in the parent. It does not include the current directory in search
        if find_in_parent:
            source.find_in_parent = True
            source.base_dir = find_tackle_base_in_parent_dir_with_exception(
                context=context,
                dir=os.path.abspath('..'),
            )
            source.name = os.path.basename(source.base_dir)
            update_source(
                context=context,
                source=source,
                directory=directory,
                file=file,
            )
            source.hooks_dir = find_hooks_directory_in_dir(dir=source.base_dir)
        elif not isinstance(first_arg, str):

            raise Exception(
                "We should not be here - first arg should have been put as ref to"
                "something that can be parsed. If it is not string, then it should be "
                "put as the raw_input and call it a day - ie return data? But that does "
                "not work in our factory..."
            )

        # Zipfile
        elif first_arg.lower().endswith('.zip'):
            source.base_dir = unzip(
                zip_uri=first_arg,
                clone_to_dir=settings.tackle_dir,
                no_input=context.no_input,
                # password=password,  # TODO: RM - Should prompt?
            )
            # source.name = '_'.join(first_arg.split('.')[:-1])
            source.name = format_path_to_name(path=first_arg)
            update_source(
                context=context,
                source=source,
                directory=directory,
                file=file,
            )
            source.hooks_dir = find_hooks_directory_in_dir(dir=source.base_dir)
        # Repo
        elif is_repo_url(first_arg):
            if latest:
                checkout = 'latest'
            source.base_dir = get_repo_source(
                repo=first_arg,
                repo_version=checkout,
            )
            source.name = first_arg.replace('/', '_')
            update_source(
                context=context,
                source=source,
                directory=directory,
                file=file,
            )
            source.hooks_dir = find_hooks_directory_in_dir(dir=source.base_dir)
        # Directory
        elif is_directory_with_tackle(first_arg):
            # Special case where the input is a path to a directory with a provider
            source.base_dir = os.path.abspath(first_arg)
            # source.name = os.path.basename(source.base_dir)
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
            source.file = os.path.basename(file_path)
            source.directory = source.base_dir = str(Path(file_path).parent.absolute())
            # source.name = '_'.join(source.file.split('.')[:-1])
            source.name = format_path_to_name(path=source.base_dir)
            source.hooks_dir = find_hooks_directory_in_dir(dir=str(source.base_dir))
        else:
            # Tackle has been called without an arg that could be recognized as a source
            # so we need to check if there is a tackle file in the current or parent
            # directory and if there is, use that as source and don't consume the arg.
            # Will raise error later if the arg was not used.
            context.input.args.insert(0, first_arg)
            source.base_dir = find_tackle_base_in_parent_dir(dir=os.path.abspath('.'))
            if source.base_dir is None:
                # We don't have a tackle base
                source.base_dir = os.path.abspath('.')
            # source.name = os.path.basename(source.base_dir)
            source.name = format_path_to_name(path=source.base_dir)
            update_source(
                context=context,
                source=source,
                directory=directory,
                file=file,
            )
    else:
        source.base_dir = find_tackle_base_in_parent_dir_with_exception(
            context=context,
            dir=os.path.abspath('.'),
        )
        # source.name = os.path.basename(source.base_dir)
        source.name = format_path_to_name(path=source.base_dir)
        update_source(
            context=context,
            source=source,
            directory=directory,
            file=file,
        )

    return source


def new_inputs(
        args: tuple = None,
        kwargs: dict = None,
) -> InputArguments:
    """
    Create a `input` object which holds the args/kwargs to create a source and then
     get consumed by the parser.
    """
    if args == (None, ):
        # This happens when there is no input to the commandline
        args = []
    else:
        # This happens
        args = list(args)

    if kwargs is None:
        kwargs = dict()

    input_obj = InputArguments(
        args=args,
        kwargs=kwargs,
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
        # Data
        input: dict | list | None = None,
        overrides: Union[str, dict] = None,
        existing_data: str | dict | None = None,
        # Context
        no_input: bool = None,
        verbose: bool = None,
        # Models -> Used when calling tackle from tackle
        _path: 'Paths' = None,
        _hooks: 'Hooks' = None,
        _data: 'Data' = None,
        # Unknown args/kwargs preserved for parsing
        **kwargs: dict,
) -> 'Context':
    """Create a new context. See tackle.main.tackle for options which wraps this."""
    print()
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
    )
    context.path = new_path(
        context=context,
        _path=_path,
    )
    context.data = new_data(
        context=context,
        input=input,
        overrides=overrides,
        existing_data=existing_data,
        _data=_data,
    )
    create_hooks(
        context=context,
        _hooks=_hooks,
        hooks_dir=hooks_dir,
    )

    return context
