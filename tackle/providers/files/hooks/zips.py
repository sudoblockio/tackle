"""Terraform hooks."""
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
import zipfile
from pydantic import Field

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class ZipHook(BaseHook):
    """Hook to zip a file or directory."""

    hook_type: str = 'zipfile'

    input: str = Field(..., description="Input path")
    output: str = Field(..., description="Output path")

    def exec(self):
        if os.path.isdir(self.input):
            zf = zipfile.ZipFile(self.output, "w", zipfile.ZIP_DEFLATED)
            for dirname, subdirs, files in os.walk(self.input):
                zf.write(dirname)
                for filename in files:
                    zf.write(os.path.join(dirname, filename))
            zf.close()
        elif os.path.isfile(self.input):
            zipfile.ZipFile(self.output, "w").write(self.input)
        else:
            raise FileNotFoundError(f"Can't find input path {self.input}.")
        return self.output


class UnzipHook(BaseHook):
    """Hook to unzip a file."""

    hook_type: str = 'unzipfile'

    input: str = Field(..., description="Input path")
    output: str = Field(".", description="Output path, default to current directory")

    def exec(self):
        if os.path.isfile(self.input):
            with zipfile.ZipFile(self.input, 'r') as zip_ref:
                zip_ref.extractall(self.output)
        else:
            raise FileNotFoundError(f"Can't find input path {self.input}.")
        return self.output
