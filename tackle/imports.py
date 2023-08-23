import os
import sys
import importlib
import logging
import subprocess
from pydantic import ValidationError, PydanticUserError
from pydantic._internal._model_construction import ModelMetaclass  # noqa

from typing import TYPE_CHECKING

from tackle import exceptions
from tackle.utils.files import read_config_file
from tackle.settings import settings
from tackle.models import BaseHook
from tackle.utils.prompts import confirm_prompt

if TYPE_CHECKING:
    from tackle.models import Context

logger = logging.getLogger(__name__)


def import_python_hooks_from_file(
        context: 'Context',
        module_name: str,
        file_path: str,
):
    loader = importlib.machinery.SourceFileLoader(module_name, path=file_path)
    if sys.version_info.minor < 10:
        mod = loader.load_module()
    else:
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        try:
            loader.exec_module(mod)
        except (ValidationError, PydanticUserError) as e:
            raise exceptions.TackleHookImportException(
                e.__str__(), context=context, file=file_path
            )
        except Exception as e:
            print(e)
            raise
    # Loop through all the module items and add the hooks
    for k, v in mod.__dict__.items():
        if (
                not k.startswith('_')
                and isinstance(v, ModelMetaclass)
                and issubclass(v, BaseHook)
                and k != 'BaseHook'
        ):
            if v.model_fields['is_public'].default:
                context.hooks.public[v.model_fields['hook_type'].default] = v
            else:
                context.hooks.private[v.model_fields['hook_type'].default] = v


def import_hooks_from_file(
        context: 'Context',
        # hooks: Hooks,
        provider_name: str,
        file_path: str,
):
    directory, filename = os.path.split(file_path)
    file_base, file_extension = os.path.splitext(filename)
    file_extension = file_extension[1:]

    if file_extension == '':
        return
    if file_base in ('pre_gen_project', 'post_gen_project', '__pycache__'):
        # Maintaining cookiecutter support here as it might have a `hooks` dir.
        return
    elif file_extension == 'pyc':
        return
    elif file_extension in ('yaml', 'yml', 'json', 'toml'):
        from tackle.parser import parse_context

        file_contents = read_config_file(
            file=file_path,
            file_extension=file_extension
        )
        if file_contents is None:
            logger.debug(f"Skipping importing {file_path} as the context is empty.")
            return
        old_raw_input = context.data.raw_input
        context.data.raw_input = file_contents
        parse_context(context=context, call_hooks=False)
        context.data.raw_input = old_raw_input

    elif file_extension == "py":
        module_name = provider_name + '.hooks.' + file_base
        import_python_hooks_from_file(
            context=context,
            module_name=module_name,
            file_path=file_path,
        )
        # try:
        #     module_name = provider_name + '.hooks.' + file_base
        # except Exception as e:
        #     print(e)
        #     pass
        # loader = importlib.machinery.SourceFileLoader(module_name, path=file_path)
        # if sys.version_info.minor < 10:
        #     mod = loader.load_module()
        # else:
        #     spec = importlib.util.spec_from_loader(loader.name, loader)
        #     mod = importlib.util.module_from_spec(spec)
        #     sys.modules[spec.name] = mod
        #     try:
        #         loader.exec_module(mod)
        #     except (ValidationError, PydanticUserError) as e:
        #         raise exceptions.TackleHookImportException(
        #             e.__str__(), context=context, file=file_path
        #         )
        #     except Exception as e:
        #         print(e)
        #         raise
        # # Loop through all the module items and add the hooks
        # for k, v in mod.__dict__.items():
        #     if (
        #             not k.startswith('_')
        #             and isinstance(v, ModelMetaclass)
        #             and issubclass(v, BaseHook)
        #             and k != 'BaseHook'
        #     ):
        #         if v.model_fields['is_public'].default:
        #             context.hooks.public[v.model_fields['hook_type'].default] = v
        #         else:
        #             context.hooks.private[v.model_fields['hook_type'].default] = v


# def get_hooks_from_hooks_init(
#         provider_name: str,
#         hooks_directory: str,
# ) -> Optional[dict[str, LazyImportHook]]:
#     hooks_init_path = os.path.join(hooks_directory, '__init__.py')
#     hooks_dict = None
#     if os.path.isfile(hooks_init_path):
#         hooks_dict = {}
#         loader = importlib.machinery.SourceFileLoader(
#             provider_name,
#             path=hooks_init_path,
#         )
#         mod = loader.load_module()
#         hook_types = getattr(mod, 'hook_types', [])
#         for h in hook_types:
#             new_hook = LazyImportHook(
#                 hooks_path=hooks_directory,
#                 mod_name=provider_name,
#                 provider_name=provider_name,
#                 hook_type=h,
#             )
#             hooks_dict[h] = new_hook
#     return hooks_dict


def import_hooks_from_hooks_directory(
        context: 'Context',
        # hooks: Hooks,
        provider_name: str,
        hooks_directory: str,
):
    # Import hooks from __init__.py per convention. See docs.
    # init_hooks = get_hooks_from_hooks_init(
    #     provider_name=provider_name,
    #     hooks_directory=hooks_directory
    # )
    # if init_hooks is not None:
    #     # TODO: Once implementing a cache / freeze option change this so it can set
    #     #  either public or private hooks
    #     hooks.private.update(init_hooks)
    #     # If there is an __init__.py with hooks defined in it we stop importing right
    #     # away and assume that we don't need to proceed.
    #     return

    for file in os.scandir(hooks_directory):
        import_hooks_from_file(
            context=context,
            # hooks=hooks,
            provider_name=provider_name,
            file_path=file.path,
        )


def import_native_providers(context: 'Context'):
    """
    Import the native providers. First qualifies if we are running locally (ie the
     `local_install` setting is active in which case we need to manually import all the
      native provides. Otherwise just use the cached native providers as we would under
      normal runs. Importing providers adds about .7 seconds each time we run tackle.
    """
    native_providers_directory = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'providers'
    )
    if settings.local_install:
        for i in os.scandir(native_providers_directory):
            if i.is_dir() and i.name != '__pycache__':
                import_hooks_from_hooks_directory(
                    context=context,
                    hooks_directory=os.path.join(i.path, 'hooks'),
                    provider_name=i.name,
                )
    else:
        raise NotImplemented


def install_requirements_file(requirements_path: str):
    """Does title..."""
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "--disable-pip-version-check",
            "-r",
            requirements_path,
        ]
    )


def install_reqs_with_prompt(
        context: 'Context',
        provider_name: str,
        requirements_path: str,
):
    """Checks settings and then potentially prompts user for installing requirements."""
    if context.no_input or not settings.prompt_for_installs:
        install_requirements_file(requirements_path=requirements_path)
    else:
        requirements = []
        with open(requirements_path, 'r') as file:
            for line in file:
                line = line.strip()  # remove trailing and leading white space
                if line:  # skip empty lines
                    if line.startswith('#'):  # skip comments
                        continue
                    # remove version and comments
                    requirement = line.split('==')[0].split('#')[0].strip()
                    requirements.append(requirement)
        install_ok = confirm_prompt(
            f"The provider {provider_name} has some requirements including"
            f" {' '.join(requirements)}. Ok to install?"
        )
        if install_ok:
            install_requirements_file(requirements_path=requirements_path)
        else:
            logger.info(f"Did not install requirement for provider {provider_name}."
                        f" Exiting...")
            sys.exit(0)


def fallback_install_then_import(
        context: 'Context',
        provider_name: str,
        hooks_directory: str,
):
    # We want to make this relative to the hooks directory as it is detected earlier
    # ie (hooks vs .hooks or specified)
    requirements_path = os.path.join(hooks_directory, '..', 'requirements.txt')
    if os.path.isfile(requirements_path):
        # It is a convention of providers to have a requirements file at the base.
        # Install the contents if there was an import error
        install_reqs_with_prompt(
            context=context,
            provider_name=provider_name,
            requirements_path=requirements_path,
        )
    import_hooks_from_hooks_directory(
        context=context,
        provider_name=provider_name,
        hooks_directory=hooks_directory,
    )


def import_with_fallback_install(
        context: 'Context',
        provider_name: str,
        hooks_directory: str,
        # hooks: 'Hooks' = None,
        # skip_on_error: bool = False,
):
    """
    Import a module and on import error, fallback on requirements file and try to
     import again.
    """
    try:
        import_hooks_from_hooks_directory(
            context=context,
            provider_name=provider_name,
            hooks_directory=hooks_directory,
        )
    except ModuleNotFoundError:
        fallback_install_then_import(
            context=context,
            provider_name=provider_name,
            hooks_directory=hooks_directory,
        )
