from typing import Type

from pydantic import BaseModel

from tackle import BaseHook, HookCallInput
from tackle.pydantic.config import DclHookModelConfig
from tackle.pydantic.field_types import FieldInput

MODELS = [
    BaseHook,
    HookCallInput,
    FieldInput,
    DclHookModelConfig,
]


class ModelOutput(BaseModel):
    name: str
    description: str | None
    type: str


class GetModelData(BaseHook):
    """Get all the data out of models so that we can render documentation."""

    hook_name = 'model_data'

    def extract_model_data(self, model: Type[BaseModel]) -> dict[str, ModelOutput]:
        model_output = {}
        for k, v in model.model_fields.items():
            try:
                model_output[k] = ModelOutput(
                    name=k,
                    description=v.description,
                    type=v.annotation.__repr__(),
                )
            except TypeError:
                model_output[k] = ModelOutput(
                    name=k,
                    description=v.description,
                    type=v.annotation.__name__,
                )
        return model_output

    def exec(self) -> dict:
        output = {}
        for M in MODELS:
            output[M.__name__] = self.extract_model_data(M)

        return output
