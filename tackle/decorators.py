from pydantic.fields import FieldInfo
from tackle.pydantic.create_model import create_model
from tackle import Context, exceptions

from inspect import signature, currentframe, Parameter
from typing import Any, TypeVar, Callable

from tackle.imports import PyImportContext
from tackle.models import BaseHook, HookCallInput

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


def hook(*, is_public: bool = False, name: str = None):
    def decorator(func: Callable):
        func_name = name or func.__name__
        sig = signature(func)

        # Known injectable types (you can extend this freely)
        known_injectables: dict[type, Callable[..., Any]] = {
            Context: lambda ctx, _: ctx,
            HookCallInput: lambda _, hc: hc,
        }

        # Find which args are injectable
        injectable_params: dict[str, type] = {}
        standard_params: list[str] = []

        for param in sig.parameters.values():
            # skip 'self', not relevant here
            if param.name == 'self':
                continue
            annotation = param.annotation
            if annotation in known_injectables or str(annotation) in {"Context",
                                                                      "HookCallInput"}:
                injectable_params[param.name] = annotation
            else:
                standard_params.append(param.name)

        # Build field defs for Pydantic
        field_defs = {
            param.name: (
                param.annotation if param.annotation is not Parameter.empty else Any,
                param.default if param.default is not Parameter.empty else ...
            )
            for param in sig.parameters.values()
            if param.name in standard_params
        }

        # Required tackle metadata
        field_defs["args"] = (list[str], standard_params)
        field_defs["help"] = (str, func.__doc__)

        # Create model
        HookCls = create_model(
            func_name,
            __base__=BaseHook,
            __config__=None,
            **field_defs,
        )

        HookCls.__is_public__ = is_public
        HookCls.__public_methods__ = []
        HookCls.__private_methods__ = []
        HookCls.hook_name = func_name
        HookCls.__provider_name__ = "inline"

        # Attach generic exec
        def _exec(self, context: Context, hook_call: HookCallInput):
            kwargs: dict[str, Any] = {}

            # Inject all standard fields
            for param in standard_params:
                kwargs[param] = getattr(self, param)

            # Inject known runtime parameters
            for param_name, annotation in injectable_params.items():
                if annotation in (Context, 'Context'):
                    injectable_value = context
                elif annotation in (HookCallInput, 'HookCallInput'):
                    injectable_value = hook_call
                else:
                    raise RuntimeError(f"Unsupported injectable type: {annotation}")
                kwargs[param_name] = injectable_value

            return func(**kwargs)

        setattr(HookCls, "exec", _exec)

        return HookCls

    return decorator
