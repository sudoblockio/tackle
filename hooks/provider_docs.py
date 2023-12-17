import os
import sys
import random
import string
import importlib.machinery
import json
from types import UnionType

from pydantic import BaseModel, Field
import inspect
from typing import List, get_type_hints, Any, Union, Optional

from tackle import exceptions, Context
from tackle.utils.type_strings import type_to_string

try:
    from typing import _GenericAlias
except ImportError:
    pass

from tackle.utils.paths import listdir_absolute
from tackle.models import BaseHook


class HookDocField(BaseModel):
    """Class for params in a hook."""

    name: str
    required: bool
    type: str
    default: Any = ""
    description: str = ""


class HookArgField(BaseModel):
    """Class for args in a hook."""

    argument: str
    type: str


class HookDoc(BaseModel):
    """Class for a hook doc."""

    hook_name: str
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


# def type_to_string(type_) -> str:
#     """Convert hook ModelField type_ to string."""
#     if type_ == Any:
#         output = 'any'
#     elif isinstance(type_, _GenericAlias):
#         if isinstance(type_, List):
#             output = 'list'
#         else:
#             output = 'union'
#     elif isinstance(type_, UnionType):
#         if isinstance(type_, List):
#             output = 'list'
#         else:
#             output = 'union'
#     else:
#         output = type_.__name__
#     return output


def get_hook_properties(hook) -> List[HookDocField]:
    """Get the input params for a hook."""
    # Get the base properties like `for` and `if` so they can be ignored
    basehook_properties = BaseHook(hook_name='tmp').model_fields

    output = []
    for k, v in hook.__fields__.items():
        # Ignored properties
        if k in basehook_properties:
            continue

        # Type is dealt with elsewhere
        if k == 'hook_name':
            continue

        # Skip properties ending with "_" as these don't need documentation
        if k.endswith("_"):
            continue

        hook_doc = HookDocField(
            name=k,
            required=v.default is not None,
            type=type_to_string(v.annotation),
            default=v.default,
            description=v.description
            if v.description is not None
            else "",
        )
        output.append(hook_doc)
    return output


def get_hook_arguments(hook: BaseHook) -> List[HookArgField]:
    """Get the arguments for a hook."""
    output = []

    for i in hook.model_fields['args'].default:
        try:
            type_ = type_to_string(hook.model_fields[i].annotation)
        except KeyError as e:
            raise e
        except Exception as e:
            print(f"{e}")
            raise e
        output.append(
            HookArgField(
                argument=i,
                type=type_,
            )
        )

    return output


def get_private_model_field(hook: BaseHook, field_name: str, default: Any = None):
    if field_name in hook.model_fields:
        return hook.model_fields[field_name].default
    return default


class ProviderDocsHook(BaseHook):
    """Hook for extracting provider metadata for building docs."""

    hook_name: str = "provider_docs"

    # fmt: off
    path: str = Field(".", description="The path to the provider.")
    # output: str = Field(".", description="The path to output the docs to.")
    provider: str = Field(None, description="The provider name.")
    hooks_dir: str = Field("hooks", description="Directory hooks are in.")
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

    def exec(self, context: Context) -> Union[dict, list]:
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
                if '_wip' in h.model_fields and h.model_fields['_wip'].default:
                    continue
                try:
                    return_type = get_type_hints(h.exec)
                except NameError as e:
                    raise e
                if 'return' in return_type:
                    return_type = type_to_string(return_type['return'])
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
                        hook_name=inspect.signature(h).parameters['hook_name'].default,
                        # In markdown tables, new lines get messed up so replace with html
                        description=schema['description'].replace("\n\n",
                                                                  "<br />").replace(
                            "\n", "")
                        if 'description' in schema
                        else "",
                        return_type=return_type,
                        # return_description=h._return_description,
                        return_description=get_private_model_field(h, '_return_description'),
                        hook_file_name=os.path.basename(f),
                        # doc_tags=h._doc_tags,
                        # issue_numbers=h._issue_numbers,
                        # notes=h._notes,
                        # order=h._docs_order,
                        doc_tags=get_private_model_field(h, '_doc_tags', []),
                        issue_numbers=get_private_model_field(h, '_issue_numbers', []),
                        notes=get_private_model_field(h, '_notes', []),
                        order=get_private_model_field(h, '_docs_order', 5),
                    )
                    docs.hooks.append(hook_doc)

        # Sort based on order
        # Sort alphabetically
        docs.hooks = sorted(docs.hooks, key=lambda d: d.hook_name)

        if self.output_schemas:
            return schema_list
        else:
            return docs.dict()
