from tackle.exceptions import TackleHookCallException


class UndefinedVariableInTemplate(TackleHookCallException):
    """
    Exception for out-of-scope variables.

    Raised when a template uses a variable which is not defined in the
    context.
    """


class GenerateHookTemplateNotFound(TackleHookCallException):
    """
    Exception when template is not found.

    Raised when can't find the template to render.
    """
