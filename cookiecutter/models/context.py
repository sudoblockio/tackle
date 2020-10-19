from pydantic import BaseModel
from typing import Dict, Any
from collections import OrderedDict
import os


class Context(BaseModel):
    context_file: str = None
    context_key: str = os.path.basename(context_file).split('.')[0]

    existing_context: Dict = None
    extra_context: Dict = None

    context_dict: OrderedDict = None

    def __init__(self, **data: Any):
        super().__init__(**data)
