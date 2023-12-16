from typing import Type, Optional
from pydantic import BaseModel, field_validator

from tackle import BaseHook, Context

MODELS = [
    BaseHook,
    Context,
]


class ModelOutput(BaseModel):
    name: str
    description: Optional[str]
    type: str


class GetModelData(BaseHook):
    """Get all the data out of models so that we can render documentation."""
    hook_name: str = 'model_data'

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
        output[BaseHook.__name__] = self.extract_model_data(BaseHook)



        return output
