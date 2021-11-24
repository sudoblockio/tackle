# -*- coding: utf-8 -*-
import pygohcl
from tackle.models import BaseHook, Field


class HclHook(BaseHook):
    """Hook for HCL (Hashicorp Configuration Language)."""

    type: str = 'hcl'

    path: str = Field(..., description="The file path to read hcl file from.")

    def execute(self):

        with open(self.path) as f:
            output = pygohcl.loads(f)
        return output
