"""All exceptions are defined here."""
import inspect
import os
import sys
from typing import TYPE_CHECKING

from tackle.utils.dicts import get_readable_key_path

if TYPE_CHECKING:
    from typing import Type, Union
    from pydantic.main import ModelMetaclass
    from tackle.models import Context, BaseFunction, BaseHook, BaseContext


def raise_unknown_hook(context: 'Context', hook_type: str, method: bool = None):
    """Raise an exception for when there is a missing hook with some context."""
    if method:
        type_ = ["method", "hook"]
        extra = ""  # TODO
        # extra = "Available methods include"
    else:
        type_ = ["hook", "providers"]
        if context.verbose:
            available_hooks = "".join(
                sorted([str(i) for i in context.provider_hooks.keys()])
            )
            extra = f'Available hooks = {available_hooks}'

        else:
            extra = "Run the application with `--verbose` to see available hook types."

    raise UnknownHookTypeException(
        f"The {type_[0]}=\"{hook_type}\" is not available in the {type_[1]}. " + extra,
        context=context,
    )


class ContributionNeededException(Exception):
    """
    Special exception to point users (particularly of the Windows variety) to contribute
     a fix with context that includes a link to the file needing upgrade.
    """

    def __init__(self, extra_message=None):
        # self.path_to_code = link_to_code
        self.extra_message = extra_message
        self.message = (
            f"Unimplemented / needs to be built "
            f"- PLEASE HELP -> "
            f"https://github.com/robcxyz/tackle/blob/main/{self.file_location()}"
            f"\n{self.extra_message}"
        )
        super().__init__(self.message)

    def __new__(cls, *args, **kwargs):
        new_instance = super(ContributionNeededException, cls).__new__(
            cls, *args, **kwargs
        )
        stack_trace = inspect.stack()
        created_at = '%s:%d' % (stack_trace[1][1], stack_trace[1][2])
        new_instance.created_at = created_at
        return new_instance

    def file_location(self):
        path_list = os.path.normpath(self.created_at).split(os.sep)
        for i, v in enumerate(path_list):
            if v == 'tackle':
                break
        github_path_list = path_list[i:-1] + [
            path_list[-1].split(':')[0] + "#L" + path_list[-1].split(':')[1]
        ]
        return os.path.join(*github_path_list)


#
# Base exceptions - Ones that are subclassed later
#


class TackleHookCallException(Exception):
    """Base hook call exception class. Subclassed within providers."""

    def __init__(self, extra_message: str, hook: 'Type[BaseHook]' = None):
        self.message = (
            f"Error parsing input_file='{hook.calling_file}' at "
            f"key_path='{get_readable_key_path(key_path=hook.key_path)}' \n"
            f"{extra_message}"
        )
        if not hook.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


class HookUnknownChdirException(TackleHookCallException):
    """
    Exception for a hook call with a chdir method.

    Raised when chdir is to an unknown directory.
    """


#
# Function call exceptions
#
class TackleFunctionCallException(Exception):
    """Base hook call exception class."""

    def __init__(
        self,
        extra_message: str,
        function: 'Union[BaseFunction, Type[ModelMetaclass]]',
    ):
        self.message = (
            f"Error parsing input_file='{function.calling_file}' at "
            f"key_path='{get_readable_key_path(key_path=function.key_path)}' \n"
            f"{extra_message}"
        )
        if not function.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


class FunctionCallException(TackleFunctionCallException):
    """
    Exception for when walking a function input context.

    Raised in function calls.
    """


#
# Parser exceptions
#
class TackleParserException(Exception):
    """Base parser exception class."""

    def __init__(self, extra_message: str, context: 'Union[Context, BaseContext]'):
        self.message = (
            f"Error parsing input_file='{context.current_file}' at "
            f"key_path='{get_readable_key_path(key_path=context.key_path)}' \n"
            f"{extra_message}"
        )
        if not context.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


class HookCallException(TackleParserException):
    """
    Exception for an unknown field in a hook.

    Raised when field has been provided not declared in the hook type.
    """


class HookParseException(TackleParserException):
    """
    Exception for an unknown field in a hook.

    Raised when field has been provided not declared in the hook type.
    """


class AppendMergeException(TackleParserException):
    """
    Excpetion when user tries to merge from for loop (ie hook --for [] --merge).

    Raised when merging the output of a hook call.
    """


class TopLevelMergeException(TackleParserException):
    """
    Excpetion when user tries to merge from top level (ie t->: literal foo --merge).

    Raised when merging the output of a hook call.
    """


class EmptyBlockException(TackleParserException):
    """
    Exception when a block (ie a compact hook without a hook type - key->: if:/for:)
    is declared without any contents.

    Raised when handling empty blocks.
    """


class UnknownArgumentException(TackleParserException):
    """
    Exception unknown argument when supplied via a hook call.

    Raised when a hook is called with an unknown argument in it's mapping (ie missing
    `_args` param in the hook definition.
    """


class UnknownTemplateVariableException(TackleParserException):
    """
    Exception for an unknown templatable argument.

    Raised when rendering variables.
    """


class MissingTemplateArgsException(TackleParserException):
    """
    Exception with missing arguments in hook call within template.

    Raised when rendering variables.
    """


class TooManyTemplateArgsException(TackleParserException):
    """
    Exception with missing arguments in hook call within template.

    Raised when rendering variables.
    """


class UnknownHookTypeException(TackleParserException):
    """
    Exception for unknown hook type.

    Raised when a hook type is not available from the providers.
    """


class MalformedTemplateVariableException(TackleParserException):
    """
    Exception for a malformed templatable argument.

    Raised when rendering variables.
    """


#
# Parser input exceptions
#
class TackleParserInputException(Exception):
    """Base input parser exception class."""

    def __init__(self, extra_message: str, context: 'Context' = None):
        self.message = (
            f"Error parsing input_file='{context.input_file}' \n" f"{extra_message}"
        )
        if not context.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


# class TackleFileInitialParsingException(TackleParserInputException):
#     """
#     Exception when base tackle file is empty.
#
#     Raised when calling files / providers.
#     """


class EmptyTackleFileException(TackleParserInputException):
    """
    Exception when base tackle file is empty.

    Raised when calling files / providers.
    """


class UnknownSourceException(TackleParserInputException):
    """
    Exception for ambiguous source.

    Raised when tackle cannot determine which directory is the project
    template, e.g. more than one dir appears to be a template dir.
    """


class UnknownInputArgumentException(TackleParserInputException):
    """
    Exception for unknown extra arguments.

    Raised when tackle cannot determine what the extra argument means.
    """


#
# Util exceptions -> No context
#
class TackleException(Exception):
    """
    Base exception class.

    All Tackle-specific exceptions should subclass this class.
    """

    def __init__(self, message: str):
        self.message = message
        sys.tracebacklimit = 0
        super().__init__(self.message)


class InvalidConfiguration(TackleException):
    """
    Exception for invalid configuration file.

    Raised if the global configuration file is not valid YAML or is
    badly constructed.
    """


# class UnknownRepoType(TackleException):
#     """
#     Exception for unknown repo types.
#
#     Raised if a repo's type cannot be determined.
#     """


class VCSNotInstalled(TackleException):
    """
    Exception when version control is unavailable.

    Raised if the version control system (git or hg) is not installed.
    """


class VersionNotFoundError(TackleException):
    """
    Exception when a version to a provider is given but does not exist.

    Raised if a version is specified but does not exist on the remote.
    """


class UnsupportedBaseFileTypeException(TackleException):
    """
    Exception for when a none json / yaml file are read

    Raised if the base file that is being called is not json / yaml.
    """


class ContextDecodingException(TackleException):
    """
    Exception for failed JSON decoding.

    Raised when a project's JSON context file can not be decoded.
    """


class RepositoryNotFound(TackleException):
    """
    Exception for missing repo.

    Raised when the specified tackle repository doesn't exist.
    """


class ContextFileNotFound(TackleException):
    """
    Exception for missing context file.

    Raised when the specified context file doesn't exist.
    """


class RepositoryCloneFailed(TackleException):
    """
    Exception for un-cloneable repo.

    Raised when a tackle template can't be cloned.
    """


class InvalidZipRepository(TackleException):
    """
    Exception for bad zip repo.

    Raised when the specified tackle repository isn't a valid
    Zip archive.
    """


#
# Function create exceptions
#
class TackleFunctionCreateException(Exception):
    """Base hook call exception class."""

    def __init__(
        self, extra_message: str, function_name: str, context: 'Context' = None
    ):
        self.message = (
            f"Error creating hook='{function_name}' in file="
            f"'{context.calling_file}', {extra_message}"
        )
        if not context.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


class EmptyFunctionException(TackleFunctionCreateException):
    """
    Exception when a function is declared without any input.

    Happens when a tackle file is parsed.
    """


class MalformedFunctionFieldException(TackleFunctionCreateException):
    """
    Exception when functions with field inputs of type dict are not formatted
    appropriately.

    Happens when a tackle file is parsed.
    """


class ShadowedFunctionFieldException(TackleFunctionCreateException):
    """
    Exception when functions with field inputs of type dict are not formatted
    appropriately.

    Happens when a tackle file is parsed.
    """


class TackleGeneralException(Exception):
    """Base hook call exception class."""

    def __init__(self, message: str):
        sys.tracebacklimit = 0
        super().__init__(message)


class NoInputOrParentTackleException(TackleGeneralException):
    """
    Exception when no input has been given, nor is there a parent tackle.

    Raised when a hook is called with an unknown argument in it's mapping (ie missing
    `_args` param in the hook definition.
    """


class TackleImportError(TackleGeneralException):
    """
    Exception when functions with field inputs of type dict are not formatted
    appropriately.

    Happens when a tackle file is parsed.
    """


class TackleFileInitialParsingException(TackleGeneralException):
    """
    Exception when parsing a tackle file.

    Raised when first parsing a file.
    """
