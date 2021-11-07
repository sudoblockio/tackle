"""All exceptions used in the tackle box code base are defined here."""
import inspect
import os


class ContributionNeededException(Exception):
    def __init__(self):
        # self.path_to_code = link_to_code
        self.message = f"Unimplemented / needs to be built - PLEASE HELP -> https://github.com/robcxyz/tackle-box/blob/main/{self.file_location()}"
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


class TackleException(Exception):
    """
    Base exception class.

    All Tackle-specific exceptions should subclass this class.
    """


class NonTemplatedInputDirException(TackleException):
    """
    Exception for when a project's input dir is not templated.

    The name of the input directory should always contain a string that is
    rendered to something else, so that input_dir != output_dir.
    """


class UnknownTemplateDirException(TackleException):
    """
    Exception for ambiguous project template directory.

    Raised when Tackle cannot determine which directory is the project
    template, e.g. more than one dir appears to be a template dir.
    """

    # unused locally


class MissingProjectDir(TackleException):
    """
    Exception for missing generated project directory.

    Raised during cleanup when remove_repo() can't find a generated project
    directory inside of a repo.
    """

    # unused locally


class ConfigDoesNotExistException(TackleException):
    """
    Exception for missing config file.

    Raised when get_config() is passed a path to a config file, but no file
    is found at that path.
    """


class InvalidConfiguration(TackleException):
    """
    Exception for invalid configuration file.

    Raised if the global configuration file is not valid YAML or is
    badly constructed.
    """


class UnknownRepoType(TackleException):
    """
    Exception for unknown repo types.

    Raised if a repo's type cannot be determined.
    """


class VCSNotInstalled(TackleException):
    """
    Exception when version control is unavailable.

    Raised if the version control system (git or hg) is not installed.
    """


class ContextDecodingException(TackleException):
    """
    Exception for failed JSON decoding.

    Raised when a project's JSON context file can not be decoded.
    """


class OutputDirExistsException(TackleException):
    """
    Exception for existing output directory.

    Raised when the output directory of the project exists already.
    """


class InvalidModeException(TackleException):
    """
    Exception for incompatible modes.

    Raised when tackle is called with both `no_input==True` and
    `replay==True` at the same time.
    """


class FailedHookException(TackleException):
    """
    Exception for hook failures.

    Raised when a hook script fails.
    """


class UndefinedVariableInTemplate(TackleException):
    """
    Exception for out-of-scope variables.

    Raised when a template uses a variable which is not defined in the
    context.
    """

    def __init__(self, message, error, context):
        """Exception for out-of-scope variables."""
        self.message = message
        self.error = error
        self.context = context

    def __str__(self):
        """Text representation of UndefinedVariableInTemplate."""
        return (
            "{self.message}. "
            "Error message: {self.error.message}. "
            "Context: {self.context}"
        ).format(**locals())


class UnknownExtension(TackleException):
    """
    Exception for un-importable extention.

    Raised when an environment is unable to import a required extension.
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


class InvalidOperatorType(TackleException):
    """
    Exception for bad zip repo.

    Raised when the specified tackle repository isn't a valid
    Zip archive.
    """


class EscapeOperatorException(TackleException):
    """
    Exception for bad zip repo.

    Raised when the specified tackle repository isn't a valid
    Zip archive.
    """


class HookCallException(TackleException):
    """
    Exception for when a unknown field in a hook.

    Raised when field has been provided not declared in the hook type.
    """


class UnknownHookTypeException(TackleException):
    """
    Exception for unknown hook type.

    Raised when a hook type is not available from the providers.
    """


class Exception(TackleException):
    """
    Exception for unknown hook type.

    Raised when a hook type is not available from the providers.
    """


class EscapeHookException(TackleException):
    """
    Exception for when general hook errors.

    Raised in hooks.
    """
