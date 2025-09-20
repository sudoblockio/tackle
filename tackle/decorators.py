from __future__ import annotations

import inspect
from inspect import currentframe, signature, Parameter
from typing import Any, Callable, TypeVar, overload

from tackle.imports import PyImportContext
from tackle.models import BaseHook, HookCallInput
from tackle.pydantic.create_model import create_model
from tackle import Context

T = TypeVar("T", bound=Callable[..., Any])


def _is_hook_or_method(obj: Any) -> bool:
    if inspect.isclass(obj) and issubclass(obj, BaseHook):
        return True
    if inspect.isfunction(obj):
        return '.' not in obj.__qualname__
    if inspect.ismethod(obj):
        return False
    return True


def _importing_module_globals() -> dict[str, Any] | None:
    f = currentframe()
    while f:
        g = f.f_globals
        if PyImportContext.key in g:
            return g
        f = f.f_back
    return None


def _bind_into_module(cls: type[BaseHook]) -> None:
    g = _importing_module_globals() or cls.__dict__.get("__globals__", None)
    if g is None:
        return
    mod_name = g.get("__name__")
    if isinstance(mod_name, str):
        cls.__module__ = mod_name
    g[cls.hook_name] = cls


def public(func: T) -> T:
    if _is_hook_or_method(func):
        setattr(func, "__is_public__", True)
    else:
        g = _importing_module_globals()
        if g:
            ctx = g[PyImportContext.key]
            name0, name1 = func.__qualname__.split(".", 1)
            ctx.public_hook_methods.setdefault(name0, []).append(name1)
    return func


def private(func: T) -> T:
    if not _is_hook_or_method(func):
        g = _importing_module_globals()
        if g:
            ctx = g[PyImportContext.key]
            name0, name1 = func.__qualname__.split(".", 1)
            ctx.private_hook_methods.setdefault(name0, []).append(name1)
    return func


def _build_hook_from_func(
    func: Callable[..., Any],
    *,
    is_public: bool,
    name: str | None,
    help: str | None,
) -> type[BaseHook]:
    fn = name or func.__name__
    sig = signature(func)

    injectable = {
        Context: lambda ctx, _: ctx,
        HookCallInput: lambda _, hc: hc,
        "Context": lambda ctx, _: ctx,
        "HookCallInput": lambda _, hc: hc,
    }

    std_params: list[str] = []
    inj_params: dict[str, Any] = {}
    for p in sig.parameters.values():
        if p.name == "self":
            # There should be a better way than relying on self right? Or no...
            continue
        ann = p.annotation
        if (ann in injectable) or (isinstance(ann, str) and ann in injectable):
            inj_params[p.name] = ann
        else:
            std_params.append(p.name)

    field_defs: dict[str, tuple[Any, Any]] = {
        p.name: (
            (p.annotation if p.annotation is not Parameter.empty else Any),
            (p.default if p.default is not Parameter.empty else ...),
        )
        for p in sig.parameters.values()
        if p.name in std_params
    }
    field_defs["args"] = (list, std_params)
    field_defs["help"] = (str, help or func.__doc__)

    HookCls = create_model(
        fn,
        __base__=BaseHook,
        __config__=None,
        **field_defs,
    )
    HookCls.__is_public__ = is_public
    HookCls.__public_methods__ = []
    HookCls.__private_methods__ = []
    HookCls.hook_name = fn
    HookCls.__provider_name__ = "inline"  # note: double-underscore suffix

    def _exec(self, context: Context, hook_call: HookCallInput):
        kwargs: dict[str, Any] = {k: getattr(self, k) for k in std_params}
        for pn, ann in inj_params.items():
            if ann in (Context, "Context"):
                kwargs[pn] = context
            elif ann in (HookCallInput, "HookCallInput"):
                kwargs[pn] = hook_call
            else:
                raise RuntimeError(f"Unsupported injectable: {ann}")
        return func(**kwargs)

    setattr(HookCls, "exec", _exec)
    return HookCls


@overload
def hook(func: Callable[..., Any], *, is_public: bool = False,
         name: str | None = None) -> type[BaseHook]: ...


@overload
def hook(*, is_public: bool = False, name: str | None = None) -> Callable[
    [Callable[..., Any]], type[BaseHook]]: ...


def hook(
    func: Callable[..., Any] | None = None,
    *,
    is_public: bool = False,
    name: str | None = None,
    help: str | None = None,
):
    """Decorator / hook factory for making new hooks."""
    if callable(func):
        cls = _build_hook_from_func(func, is_public=is_public, name=name, help=help)
        _bind_into_module(cls)
        return cls

    def deco(f: Callable[..., Any]) -> type[BaseHook]:
        cls = _build_hook_from_func(f, is_public=is_public, name=name, help=help)
        _bind_into_module(cls)
        return cls

    return deco
