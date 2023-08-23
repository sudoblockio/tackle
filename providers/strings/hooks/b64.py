import base64

from tackle.models import BaseHook, Field


class Base64EncodeHook(BaseHook):
    """Hook for `base64_encode`. Base64 encodes a string."""

    hook_type: str = 'base64_encode'
    input: str = Field(..., description="A string to encode.")

    args: list = ['input']
    _docs_order = 8

    def exec(self) -> str:
        sample_string_bytes = self.input.encode("utf-8")
        base64_bytes = base64.b64encode(sample_string_bytes)
        base64_string = base64_bytes.decode("utf-8")
        return base64_string


class Base64DecodeHook(BaseHook):
    """Hook for `base64_decode`. Base64 decodes a string."""

    hook_type: str = 'base64_decode'
    input: str = Field(..., description="A string to decode.")

    args: list = ['input']
    _docs_order = 9

    def exec(self) -> str:
        return str(base64.b64decode(self.input).decode("utf-8"))
