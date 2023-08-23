# from tackle.models import BaseHook, Field
# from requests import get
#
# class GitHubRawHook(BaseHook):
#     """
#     Hook for github raw content.
#     """
#
#     hook_type: str = 'github_raw'
#
#     org: str = Field(None, description="The github username or org.")
#     repo: str = Field(None, description="The repo name.")
#     file_path: str = Field(None, description="")
#
#     output_path: str = Field(None, description="Optional param to take output and write to file location.")
#
#     args: list = ['org', 'repo']
#
#     def make_url(self) -> str:
#         url = f"https://raw.githubusercontent.com/{self.org}/{self.repo}/master/path/to/file "
#         return url
#
#     def make_output_path(self) -> str:
#         if self.output_path == ".":
#             self.
#
#
#     def exec(self):
#         url = self.make_url()
#         output = get(url=url)
#
#         if self.output_path is not None:
#             with open(self.output_path, 'w') as f:
#                 f.write()
#
