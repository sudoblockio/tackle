import os
import sys
import random
import string
import importlib.machinery
import json
from pydantic import BaseModel, Field
import inspect
from typing import List, get_type_hints, Any, Union, Optional

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
    return_type: Optional[str]
    return_description: Optional[str]
    hook_file_name: str
    doc_tags: list
    issue_numbers: list
    notes: list
    order: int


class ProviderDocs(BaseModel):
    """Class for a provider hook."""

    name: str = None
    hooks: List[HookDoc] = []
    requirements: list = []
    description: str = None


def hook_type_to_string(type_) -> str:
    """Convert hook ModelField type_ to string."""
    if type_ == Any:
        output = 'any'
    elif isinstance(type_, _GenericAlias):
        if isinstance(type_, List):
            output = 'list'
        else:
            output = 'union'
    else:
        output = type_.__name__
    return output


def get_hook_properties(hook) -> List[HookDocField]:
    """Get the input params for a hook."""
    # Get the base properties like `for` and `if` so they can be ignored
    basehook_properties = BaseHook(hook_type='tmp').__fields__

    output = []
    for k, v in hook.__fields__.items():
        # Ignored properties
        if k in basehook_properties:
            continue

        # Type is dealt with elsewhere
        if k == 'hook_type':
            continue

        # Skip properties ending with "_" as these don't need documentation
        if k.endswith("_"):
            continue

        hook_doc = HookDocField(
            name=k,
            required=v.required,
            type=hook_type_to_string(v.type_),
            default=v.default,
            description=v.field_info.description
            if v.field_info.description is not None
            else "",
        )
        output.append(hook_doc)
    return output


def get_hook_arguments(hook) -> List[HookArgField]:
    """Get the arguments for a hook."""
    output = []

    for i in hook.__fields__['args'].default:
        output.append(
            HookArgField(
                argument=i,
                type=hook_type_to_string(hook.__fields__[i].type_),
            )
        )

    return output


class ProviderDocsHook(BaseHook):
    """Hook for extracting provider metadata for building docs."""

    hook_type: str = "provider_docs"

    # fmt: off
    path: str = Field(".", description="The path to the provider.")
    output: str = Field(".", description="The path to output the docs to.")
    provider: str = Field(None, description="The provider name.")
    hooks_dir = Field("hooks", description="Directory hooks are in.")
    output_schemas: bool = Field(False, description="Output the json schema instead.")
    # fmt: on

    args: list = ['path', 'output']
    _doc_tags: list = ["experimental"]
    _docs_order = 11
    _return_description = (
        "Returns a dictionary with metadata about a provider and "
        "it's hooks or a list of schemas when run with "
        "`output_schemas`."
    )

    def check_python_version(self):
        """Doesn't work on py3.6."""
        if sys.version_info.minor <= 6:
            raise Exception("Can't run provider_docs hook in a py version < 3.7.")

    def exec(self) -> Union[dict, list]:
        """Build the docs."""
        if not self.provider:
            self.provider = os.path.basename(os.path.abspath(self.path))

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
        schema_list = []
        for i, f in enumerate(importable_files):
            # Extract out the objects that are derived from the BaseHook
            # We generate a random name because we run this multiple times and getting
            # overlapping pydantic validator config error otherwise.
            random_name = ''.join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            loader = importlib.machinery.SourceFileLoader(fullname=random_name,
                                                          path=f)
            module_classes = inspect.getmembers(loader.load_module(), inspect.isclass)
            hooks = [
                i[1]
                for i in module_classes
                if issubclass(i[1], BaseHook) and i[1] != BaseHook
            ]
            # fmt: on

            for h in hooks:
                if h._wip:
                    continue

                return_type = get_type_hints(h.exec)
                if 'return' in return_type:
                    return_type = hook_type_to_string(return_type['return'])
                else:
                    return_type = None

                # Generate the json schema
                # schema = json.loads(h.schema_json(exclude={'default_hook'}))
                schema = json.loads(h.schema_json())
                if self.output_schemas:
                    schema_list.append(schema)
                else:
                    # Generate the docs object
                    hook_doc = HookDoc(
                        properties=get_hook_properties(h),
                        arguments=get_hook_arguments(h),
                        hook_type=inspect.signature(h).parameters['hook_type'].default,
                        # In markdown tables, new lines get messed up so replace with html
                        description=schema['description'].replace("\n\n",
                                                                  "<br />").replace(
                            "\n", "")
                        if 'description' in schema
                        else "",
                        return_type=return_type,
                        return_description=h._return_description,
                        hook_file_name=os.path.basename(f),
                        doc_tags=h._doc_tags,
                        issue_numbers=h._issue_numbers,
                        notes=h._notes,
                        order=h._docs_order,
                    )
                    docs.hooks.append(hook_doc)

        # Sort based on order
        # Sort alphabetically
        docs.hooks = sorted(docs.hooks, key=lambda d: d.hook_type)

        if self.output_schemas:
            return schema_list
        else:
            return docs.dict()
