"""All exceptions used in the tackle box code base are defined here."""
import inspect
import os
import sys
from typing import TYPE_CHECKING

from tackle.utils.dicts import get_readable_key_path

if TYPE_CHECKING:
    from typing import Type
    from tackle.models import Context, BaseHook, BaseFunction


#
# Base exceptions - Ones that are subclassed later
#
class ContributionNeededException(Exception):
    """
    Special exception to point users (particularly of the windows variety) to contribute
    a fix with context that includes a link to the file needing upgrade.
    """

    def __init__(self, extra_message=None):
        # self.path_to_code = link_to_code
        self.extra_message = extra_message
        self.message = (
            f"Unimplemented / needs to be built "
            f"- PLEASE HELP -> "
            f"https://github.com/robcxyz/tackle-box/blob/main/{self.file_location()}"
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


# TODO: RM
class TackleException(Exception):
    """
    Base exception class.

    All Tackle-specific exceptions should subclass this class.
    """


class TackleFunctionCreateException(Exception):
    """Base hook call exception class."""

    def __init__(
        self, extra_message: str, function_name: str, context: 'Context' = None
    ):
        if context:
            self.message = (
                f"Error creating function='{function_name}' in file="
                f"'{context.calling_file}', {extra_message}"
            )
            if not context.verbose:
                sys.tracebacklimit = 0
        else:
            self.message = extra_message
        super().__init__(self.message)


class TackleFunctionCallException(Exception):
    """Base hook call exception class."""

    def __init__(self, extra_message: str, function: 'Type[BaseFunction]' = None):
        if function:
            self.message = (
                f"Error parsing input_file='{function.calling_file}' at "
                f"key_path='{get_readable_key_path(key_path=function.key_path)}' \n"
                f"{extra_message}"
            )
            if not function.verbose:
                sys.tracebacklimit = 0
        else:
            self.message = extra_message
        super().__init__(self.message)


class TackleHookCallException(Exception):
    """Base hook call exception class."""

    def __init__(self, extra_message: str, hook: 'Type[BaseHook]' = None):
        if hook:
            self.message = (
                f"Error parsing input_file='{hook.calling_file}' at "
                f"key_path='{get_readable_key_path(key_path=hook.key_path)}' \n"
                f"{extra_message}"
            )
            if not hook.verbose:
                sys.tracebacklimit = 0
        else:
            self.message = extra_message
        super().__init__(self.message)


class TackleParserException(Exception):
    """Base parser exception class."""

    def __init__(self, extra_message: str, context: 'Context' = None):
        if context:
            self.message = (
                f"Error parsing input_file='{context.current_file}' at "
                f"key_path='{get_readable_key_path(key_path=context.key_path)}' \n"
                f"{extra_message}"
            )
            if not context.verbose:
                sys.tracebacklimit = 0
        else:
            self.message = extra_message
        super().__init__(self.message)


class TackleParserInputException(Exception):
    """Base input parser exception class."""

    def __init__(self, extra_message: str, context: 'Context' = None):
        if context:
            self.message = (
                f"Error parsing input_file='{context.input_file}' \n" f"{extra_message}"
            )
            if not context.verbose:
                sys.tracebacklimit = 0
        else:
            self.message = extra_message
        super().__init__(self.message)


#
# Function call exceptions
#
class FunctionCallException(TackleFunctionCallException):
    """
    Exception for when walking a function input context.

    Raised in function calls.
    """


#
# Hook call exceptions
#
class HookCallException(TackleHookCallException):
    """
    Exception for an unknown field in a hook.

    Raised when field has been provided not declared in the hook type.
    """

    # TODO: Needed?


class HookUnknownChdirException(TackleHookCallException):
    """
    Exception for a hook call with a chdir method.

    Raised when chdir is to an unknown directory.
    """


#
# Parser exceptions
#
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


class NoInputOrParentTackleException(TackleParserException):
    """
    Exception when no input has been given, nor is there a parent tackle.

    Raised when a hook is called with an unknown argument in it's mapping (ie missing
    `_args` param in the hook definition.
    """


class UnknownTemplateVariableException(TackleParserException):
    """
    Exception an unknown templatable argument.

    Raised when rendering variables.
    """


class UnknownHookTypeException(TackleParserException):
    """
    Exception for unknown hook type.

    Raised when a hook type is not available from the providers.
    """


#
# Parser input exceptions
#
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


#
# Util exceptions
#
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
