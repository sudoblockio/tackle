from pydantic import BaseModel


class TackleLockProvider(BaseModel):
    type: str = None
    version: str = None
    path: str = None
    hooks: dict[str, TackleLockHook] = {}


class TackleLock(BaseModel):
    tackle_version: str
    provider_dir: str = None
    providers: list[TackleLockProvider] = []
    hooks: TackleLockHook = {}


class PythonRequirement(BaseModel):
    package_name: str
    version: str = 'latest'
