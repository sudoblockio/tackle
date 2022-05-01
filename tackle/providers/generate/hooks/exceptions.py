from tackle.exceptions import TackleHookCallException


class UndefinedVariableInTemplate(TackleHookCallException):
    """
    Exception for out-of-scope variables.

    Raised when a template uses a variable which is not defined in the
    context.
    """

    # def __init__(self, message, error, context):
    #     """Exception for out-of-scope variables."""
    #     self.message = message
    #     self.error = error
    #     self.context = context
    #
    # def __str__(self):
    #     """Text representation of UndefinedVariableInTemplate."""
    #     return self.message
