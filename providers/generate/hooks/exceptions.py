from tackle.exceptions import TackleHookParseException


class UndefinedVariableInTemplate(TackleHookParseException):
    """
    Exception for out-of-scope variables.

    Raised when a template uses a variable which is not defined in the
    context.
    """


class GenerateHookTemplateNotFound(TackleHookParseException):
    """
    Exception when template is not found.

    Raised when can't find the template to render.
    """
