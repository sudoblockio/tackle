from inspect import signature, currentframe
from typing import Any, TypeVar

from tackle.imports import PyImportContext
from tackle.models import BaseHook

TFunc = TypeVar("TFunc", bound=BaseHook)


def _is_hook_or_method(func: TFunc) -> bool:
    sig = signature(func)
    # Check if the first parameter is 'self' or 'cls'
    params = list(sig.parameters.values())
    if params and (params[0].name in {'self', 'cls'}):
        return False
    else:
        return True


def _get_module_globals() -> dict[str, Any]:
    """Walk the stack to find the frame where the decorator is being called."""
    frame = currentframe()
    while frame:
        # Check for the presence of right key which will always be injected into the
        # import context before the decorator runs
        if PyImportContext.key in frame.f_globals:
            return frame.f_globals
        frame = frame.f_back


def _add_method_to_module_import_context(func: TFunc, is_public: bool):
    """
    The context is injected into the import thus we can append items to it while the
     import is importing this decorated method. Later we can attach the str ref to the
     public method.
    """
    module_globals = _get_module_globals()
    module_context = module_globals[PyImportContext.key]
    name_split = func.__qualname__.split('.')
    hook_name, method_name = name_split[0], name_split[1]
    if is_public:
        if hook_name not in module_context.public_hook_methods:
            module_context.public_hook_methods[hook_name] = []
        module_context.public_hook_methods[name_split[0]].append(name_split[1])
    else:
        if hook_name not in module_context.private_hook_methods:
            module_context.private_hook_methods[hook_name] = []
        module_context.private_hook_methods[name_split[0]].append(name_split[1])


def public(func: TFunc):
    """Decorate hooks or hook methods to make them public."""
    if _is_hook_or_method(func):
        func.__is_public__ = True
    else:
        _add_method_to_module_import_context(func, is_public=True)
    return func


def private(func: TFunc):
    """
    Same as public decorator but only useful to mark methods so that they can be
     inherited by tackle hooks. Otherwise, private is the default behaviour for both
     python hooks and methods.
    """
    if not _is_hook_or_method(func):
        _add_method_to_module_import_context(func, is_public=True)
    return func
