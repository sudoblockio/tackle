import base64

from tackle import BaseHook, Field


class Base64EncodeHook(BaseHook):
    """Hook for `base64_encode`. Base64 encodes a string."""

    hook_name = 'base64_encode'
    input: str = Field(..., description="A string to encode.")

    args: list = ['input']
    _docs_order = 8

    def exec(self) -> str:
        return base64.b64encode(self.input.encode("utf-8")).decode("utf-8")


class Base64DecodeHook(BaseHook):
    """Hook for `base64_decode`. Base64 decodes a string."""

    hook_name = 'base64_decode'
    input: str = Field(..., description="A string to decode.")

    args: list = ['input']
    _docs_order = 9

    def exec(self) -> str:
        return str(base64.b64decode(self.input).decode("utf-8"))
