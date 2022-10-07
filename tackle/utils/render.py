# Moved to utils as used in models.py


def wrap_braces_if_not_exist(value):
    """Wrap with braces if they don't exist."""
    if '{{' in value and '}}' in value:
        # Already templated
        return value
    return '{{' + value + '}}'


def wrap_jinja_braces(value):
    """Wrap a string with braces so it can be templated."""
    if isinstance(value, str):
        return wrap_braces_if_not_exist(value)
    # Nothing else can be wrapped
    return value
