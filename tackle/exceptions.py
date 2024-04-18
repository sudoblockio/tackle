"""All exceptions are defined here."""
import inspect
import os
import sys
from typing import TYPE_CHECKING, Any

from tackle.utils.data_crud import get_readable_key_path

if TYPE_CHECKING:
    from tackle import BaseHook, Context

DOCS_DOMAIN = "https://sudoblockio.github.io/tackle"


def get_message_input_string(context: 'Context'):
    if context.path.current.file is None:
        return f'input_directory={context.path.current.directory}'
    return f'input_file={context.path.current.file}'


def raise_unknown_hook(context: 'Context', hook_name: str, method: bool = None):
    """Raise an exception for when there is a missing hook with some context."""
    if method:
        type_ = ["method", "hook"]
        extra = ""  # TODO
        # extra = "Available methods include"
    else:
        type_ = ["hook", "providers"]
        if context.verbose:
            available_hooks = "".join(sorted([str(i) for i in context.hooks.keys()]))
            extra = f'Available hooks = {available_hooks}'
        else:
            extra = "Run the application with `--verbose` to see available hook types."

    raise UnknownHookTypeException(
        f"The {type_[0]}=\"{hook_name}\" is not available in the {type_[1]}. " + extra,
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
            f"https://github.com/sudoblockio/tackle/blob/main/{self.file_location()}"
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


class UnknownFieldInputException(Exception):
    """
    Exception for a hook call with unknown input fields. Prints available fields for a
     hook.

    Raised when chdir is to an unknown directory.
    """

    def __init__(self, extra_message: str, context: 'Context', Hook: 'BaseHook' = None):
        self.message = (
            f"Error parsing {get_message_input_string(context=context)}' at "
            f"key_path='{get_readable_key_path(key_path=context.key_path)}' \n"
            f"{extra_message}"
        )
        if not context.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)

        # if Hook.model_fields['kwargs'].default is not None:
        #     default_kwargs = Hook.model_fields['kwargs'].default
        #     if default_kwargs not in hook_call:
        #         hook_call[default_kwargs] = {}
        #     hook_call[default_kwargs][k] = render_variable(context, v)
        #     hook_call.pop(k)
        #     # continue
        #
        # # Get a list of possible fields for hook before raising error.
        # possible_fields = [
        #     f"{key}: {value.annotation.__name__}"
        #     for key, value in Hook.model_fields.items()
        #     if key not in BaseHook.model_fields
        # ]
        # # TODO: Include link to docs -> Will need to also include provider name
        # #  and then differentiate between lazy imported hooks which already have the
        # #  provider and the ones that don't
        #
        # # TODO: Test with many types of Hooks - Lazy Function etc - I don't think
        # #  they all will resolve
        # provider_name = Hook.provider_name.title()
        # base_url = "https://sudoblockio.github.io/tackle/providers"
        # url = f"{base_url}/{provider_name}/{hook_name}/"
        # raise exceptions.UnknownInputArgumentException(
        #     f"Key={k} not in hook={hook_call['hook_name']}. Possible values are "
        #     f"{', '.join(possible_fields)}. \n\n See {url}"
        #     ,  # noqa
        #     context=context,
        # ) from None


#
# Base exceptions - Ones that are subclassed later
#


class TackleHookParseException(Exception):
    """Base hook call exception class. Subclassed within providers."""

    def __init__(self, extra_message: str, context: 'Context'):
        self.message = (
            f"Error parsing {get_message_input_string(context=context)}' at "
            f"key_path='{get_readable_key_path(key_path=context.key_path)}' \n"
            f"{extra_message}"
        )
        if not context.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


class HookUnknownChdirException(TackleHookParseException):
    """
    Exception for a hook call with a chdir method.

    Raised when chdir is to an unknown directory.
    """


#
# Function call exceptions
#
class TackleHookCallException(Exception):
    """Base hook call exception class."""

    def __init__(
        self,
        extra_message: str,
        context: 'Context',
        hook_name: str,
    ):
        self.message = (
            f"Error parsing {get_message_input_string(context=context)}' at "
            f"hook='{hook_name}' at ",
            f"key_path='{get_readable_key_path(key_path=context.key_path)}' \n"
            f"{extra_message}",
        )
        if not context.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


class DclHookCallException(TackleHookCallException):
    """
    Exception for when walking a function input context.

    Raised in function calls.
    """


class UnknownHookInputArgumentException(TackleHookCallException):
    """
    Exception for unknown extra arguments.

    Raised when tackle cannot determine what the extra argument means.
    """


#
# Parser exceptions
#
class TackleParserException(Exception):
    """Base parser exception class."""

    def __init__(self, extra_message: str, context: 'Context'):
        self.message = (
            f"Error parsing {get_message_input_string(context=context)}' at "
            f"key_path='{get_readable_key_path(key_path=context.key_path)}' \n"
            f"{extra_message}"
        )
        if not context.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


class HookCallException(TackleParserException):
    """
    Exception when calling a hook.

    Raised within a python hook.
    """


class PromptHookCallException(TackleParserException):
    """
    Exception when calling a prompt hook typically in automation.

    Raised within a python hook.
    """

    def __init__(self, context: 'Context'):
        super().__init__(
            extra_message="Error calling hook most likely due to hook being called in "
            "automation where no input was given for key. Try setting "
            "the key with an `override` if that is the case. Check: "
            "https://sudoblockio.github.io/tackle/testing-providers/#testing-tackle-scripts",  # noqa
            context=context,
        )


class HookParseException(TackleParserException):
    """
    Exception for an unknown field in a hook.

    Raised when field has been provided not declared in the hook type.
    """


def raise_hook_parse_exception_with_link(
    context: 'Context',
    Hook: 'BaseHook',
    msg: str,
):
    """
    Raise a HookParseException with an additional link to the docs if the hook is a
     native hook, otherwise just the validation error.
    """
    # TODO: Check third party
    # Check if the hook is native or declarative
    # __provider_name only attached to native hooks
    provider_name = getattr(Hook, '__provider_name', None)
    if provider_name is not None:
        # if Hook.__module__.startswith('tackle.hooks.'):
        msg += (
            f"\n Check the docs for more information on the hook -> "
            f"https://sudoblockio.github.io/tackle/providers/"
            f"{Hook.__provider_name.title()}/{Hook.hook_name}/"
        )
    raise HookParseException(str(msg), context=context) from None


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


def raise_malformed_for_loop_key(context: 'Context', raw: Any, loop_targets: Any):
    raise MalformedTemplateVariableException(
        f"The `for` field must be a list/object or string reference to a list/object. "
        f"The value {raw} is of type `{type(loop_targets).__name__}`.",
        context=context,
    ) from None


#
# Parser input exceptions
#
class TackleSourceParserException(Exception):
    """Base input parser exception class."""

    def __init__(self, message: str, context: 'Context' = None):
        self.message = message
        if not context.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


class UnknownSourceException(TackleSourceParserException):
    """
    Exception for ambiguous source.

    Raised when tackle cannot determine which directory is the project
    template, e.g. more than one dir appears to be a template dir.
    """


#
# General exceptions -> No context
#
class GeneralException(Exception):
    """
    Base exception class.

    All general exceptions not requiring context should subclass this class.
    """

    def __init__(self, message: str):
        self.message = message
        sys.tracebacklimit = 0
        super().__init__(self.message)


class NoInputOrParentTackleException(GeneralException):
    """
    Exception when no input has been given, nor is there a parent tackle.

    Raised when a hook is called with an unknown argument in it's mapping (ie missing
    `_args` param in the hook definition.
    """


class TackleImportError(GeneralException):
    """
    Exception when functions with field inputs of type dict are not formatted
    appropriately.

    Happens when a tackle file is parsed.
    """


class TackleFileInitialParsingException(GeneralException):
    """
    Exception when parsing a tackle file.

    Raised when first parsing a file.
    """


class InvalidConfiguration(GeneralException):
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


class VCSNotInstalled(GeneralException):
    """
    Exception when version control is unavailable.

    Raised if git is not installed.
    """


class InternetConnectivityError(GeneralException):
    """
    Exception when version control is unable to access the internet (ie github).

    Raised if git is unable to access a repo.
    """


class VersionNotFoundError(GeneralException):
    """
    Exception when a version to a provider is given but does not exist.

    Raised if a version is specified but does not exist on the remote.
    """


class UnsupportedBaseFileTypeException(GeneralException):
    """
    Exception for when a none json / yaml file are read

    Raised if the base file that is being called is not json / yaml.
    """


class TackleFileNotFoundError(GeneralException):
    """
    Exception for when a none json / yaml file are read

    Raised if the base file that is being called is not json / yaml.
    """


class FileLoadingException(GeneralException):
    """
    Exception for failed JSON decoding.

    Raised when a project's JSON context file can not be decoded.
    """


class GenericGitException(GeneralException):
    """
    Generic exception.

    Raised when an unknown tackle.utils.vcs error occurs.
    """


class RepositoryNotFound(GeneralException):
    """
    Exception for missing repo.

    Raised when the specified tackle repository doesn't exist.
    """


class ContextFileNotFound(GeneralException):
    """
    Exception for missing context file.

    Raised when the specified context file doesn't exist.
    """


class RepositoryCloneFailed(GeneralException):
    """
    Exception for un-cloneable repo.

    Raised when a tackle template can't be cloned.
    """


class InvalidZipRepository(GeneralException):
    """
    Exception for bad zip repo.

    Raised when the specified tackle repository isn't a valid
    Zip archive.
    """


#
# Function create exceptions
#
class BaseHookCreateException(Exception):
    """Base hook call exception class."""

    def __init__(self, extra_message: str, hook_name: str, context: 'Context' = None):
        self.message = (
            f"Error parsing {get_message_input_string(context=context)}' "
            f"creating hook='{hook_name}',\n{extra_message}"
        )
        if not context.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


class EmptyHookException(BaseHookCreateException):
    """
    Exception when a function is declared without any input.

    Happens when a tackle file is parsed.
    """


class MalformedHookFieldException(BaseHookCreateException):
    """
    Exception when functions with field inputs of type dict are not formatted
    appropriately.

    Happens when a tackle file is parsed.
    """


class ShadowedHookFieldException(BaseHookCreateException):
    """
    Exception when functions with field inputs of type dict are not formatted
    appropriately.

    Happens when a tackle file is parsed.
    """


#
# Import exceptions
#
class TackleParserInputException(Exception):
    """Base input parser exception class."""

    def __init__(self, extra_message: str, context: 'Context' = None):
        self.message = f"Error parsing  \n" f"{extra_message}"
        if not context.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


class TackleImportException(TackleImportError):
    """
    Exception when importing a tackle provider.

    Raised when first importing hooks.
    """


class BaseTackleImportException(Exception):
    """Base input parser exception class."""

    def __init__(self, extra_message: str, context: 'Context', file: str = None):
        if file is None:
            file = context.source.file
        self.message = f"Error parsing input_file='{file}' \n" f"{extra_message}"
        if not context.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


# class TackleFileInitialParsingException(BaseTackleImportException):
#     """
#     Exception when base tackle file is empty.
#
#     Raised when calling files / providers.
#     """


class EmptyTackleFileException(BaseTackleImportException):
    """
    Exception when base tackle file is empty.

    Raised when calling files / providers.
    """


class TackleHookImportException(BaseTackleImportException):
    """
    Exception for a malformed templatable argument.

    Raised when rendering variables.
    """


class TackleHookCreationException(Exception):
    """Base input parser exception class."""

    def __init__(self, extra_message: str, context: 'Context', hook_name: str):
        self.message = f"Error using hook='{hook_name}' \n" f"{extra_message}"
        if not context.verbose:
            sys.tracebacklimit = 0
        super().__init__(self.message)


class BadHookKwargsRefException(TackleHookCreationException):
    """
    Exception for mapping a hook's kwargs field to a non-dict type.

    Raised when rendering a hooks vars and unknown fields are mapped via a kwargs
     attribute which references a non-dict field.
    """


class MalformedHookDefinitionException(TackleHookCreationException):
    """
    Excepetion when there is an input param to a hook's method that is not one of
     `Context` or `HookCallInput`.

    Raised when inspecting the input to a hook that requires one of those two params
     which we inject into the method at call time since we don't want to copy the
     entirety of the var into the hook.
    """
