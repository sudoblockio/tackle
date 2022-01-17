"""
`provider_docs` hooks which gets metadata about the provider so it can be rendered in
docs hooks.
"""
import os
import sys
import importlib.machinery

import json
import inspect
from pydantic import BaseModel, Field
from typing import List, get_type_hints, Any

try:
    from typing import _GenericAlias
except ImportError:
    pass

from tackle.utils.paths import listdir_absolute
from tackle.models import BaseHook


class HookDocField(BaseModel):
    """Class for params in a hook."""

    name: str
    required: str
    type: str
    default: Any = ""
    description: str = ""


class HookArgField(BaseModel):
    """Class for args in a hook."""

    argument: str
    type: str


class HookDoc(BaseModel):
    """Class for a hook doc."""

    hook_type: str
    description: str = ""
    properties: List[HookDocField]
    arguments: List[HookArgField]
    output: str = None


class ProviderDocs(BaseModel):
    """Class for a provider hook."""

    name: str = None
    hooks: List[HookDoc] = []
    requirements: list = []
    description: str = None


def get_hook_properties(schema: dict) -> List[HookDocField]:
    """Get the input params for a hook."""
    basehook_properties = json.loads(BaseHook(hook_type='tmp').schema_json())[
        'properties'
    ]

    output = []
    for k, v in schema['properties'].items():
        if k in basehook_properties:
            continue

        # Bypass any refs
        if "$ref" in v:
            continue

        # Type is dealt with elsewhere
        if k == 'hook_type':
            continue

        hook_doc = HookDocField(
            name=k,
            required="X" if 'default' in v else "",
            type=v['type'] if 'type' in v else "Any",
            default=v['default'] if 'default' in v else "",
            description=v['description'] if 'description' in v else "",
        )
        output.append(hook_doc)
    return output


def get_hook_arguments(hook) -> List[HookArgField]:
    """Get the arguments for a hook."""
    output = []

    for i in hook._args:

        if hook.__fields__[i].type_ == Any:
            type = 'any'
        elif isinstance(hook.__fields__[i].type_, _GenericAlias):
            type = 'union'
        else:
            type = hook.__fields__[i].type_.__name__

        output.append(
            HookArgField(
                argument=i,
                type=type,
            )
        )

    return output


class ProviderDocsHook(BaseHook):
    """Hook building provider docs."""

    hook_type: str = "provider_docs"

    # fmt: off
    path: str = Field(".", description="The path to the provider.")
    output: str = Field(".", description="The path to output the docs to.")

    provider: str = Field(None, description="The provider name.")
    hooks_dir = Field("hooks", description="Directory hooks are in.")
    meta_file = Field(".tackle.meta.yaml",
                      description="A file to keep metadata about the provider. Is renedered like a tackle file. See examples.")

    templates_dir: str = Field(
        None,
        description="A path to a directory with `hook-doc.md` and `provider-doc.md`."
    )
    # fmt: on

    _args: list = ['path', 'output']

    def check_python_version(self):
        """Doesn't work on py3.6."""
        if sys.version_info.minor <= 6:
            raise Exception("Can't run provider_docs hook in a py version < 3.7.")

    def execute(self) -> dict:
        """Build the docs."""
        if not self.provider:
            self.provider = os.path.basename(os.path.abspath(self.path))

        if self.templates_dir is None:
            self.templates_dir = os.path.join(
                os.path.dirname(__file__), '..', 'templates'
            )

        requirements = []
        if os.path.exists('requirements.txt'):
            with open('requirements.txt') as f:
                requirements = f.readlines()
                requirements = [line.rstrip() for line in requirements]

        docs = ProviderDocs(
            name=self.provider,
            requirements=requirements,
        )

        # fmt: off
        path = os.path.abspath(os.path.join(self.path, self.hooks_dir))
        # Loop through python files
        importable_files = [i for i in listdir_absolute(path) if
                            i.endswith("py") and not i.endswith('__init__.py')]
        for f in importable_files:
            # Extract out the objects that are derived from the BaseHook
            loader = importlib.machinery.SourceFileLoader(fullname=f,
                                                          path=f)  # Don't really care about fullname
            module_classes = inspect.getmembers(loader.load_module(), inspect.isclass)
            hooks = [
                i[1]
                for i in module_classes
                if issubclass(i[1], BaseHook) and i[1] != BaseHook
            ]
            # fmt: on

            for h in hooks:
                # Generate the json schema
                schema = json.loads(h.schema_json())

                return_type = get_type_hints(h.execute)
                if 'return' in return_type:
                    return_type = return_type['return']
                    if isinstance(return_type, _GenericAlias):
                        # TODO: Improve to inspect union types
                        output = 'union'
                    elif return_type == Any:
                        output = Any
                    else:
                        output = return_type.__name__
                else:
                    output = None

                # Generate the docs object
                hook_doc = HookDoc(
                    properties=get_hook_properties(schema),
                    arguments=get_hook_arguments(h),
                    hook_type=inspect.signature(h).parameters['hook_type'].default,
                    description=schema['description'].replace("\n", "")
                    if 'description' in schema
                    else "",
                    output=output,
                )
                docs.hooks.append(hook_doc)

        return docs.dict()
