# from tackle.models import BaseHook, Field
#
#
# class SourceTypeHooks(BaseHook):
#     """Convert git source to/from https to ssh types."""
#
#     hook_name = "git_repository"
#
#     url: str = Field(..., description="The git URL, one of https, git, ssh.")
#
#     type: str = None
#
#     args: list = ['url']
#
#     def exec(self):
#         pass
#
