from git import Repo
from typing import Optional

from tackle.models import BaseHook, Field


class GitCloneHook(BaseHook):
    """
    Hook to create clone a repo. Wraps git python `clone`.
    [Source API](https://gitpython.readthedocs.io/en/stable/reference.html#git.repo.base.Repo.clone)
    """

    hook_type: str = 'git_clone'
    url: str = Field(
        None,
        description="valid git url - [Docs](http://www.kernel.org/pub/software/scm/git/docs/git-clone.html#URLS)",
    )
    to_path: str = Field(
        None, description="Path to which the repository should be cloned to"
    )
    progress: Optional[str] = Field(None, description="See ‘git.remote.Remote.push’.")
    env: Optional[dict] = Field(
        None,
        description="Optional dictionary containing the desired environment "
        "variables. Note: Provided variables will be used to update "
        "the execution environment for git. If some variable is not "
        "specified in env and is defined in os.environ, value from "
        "os.environ will be used. If you want to unset some "
        "variable, consider providing empty string as its value.",
    )
    multi_options: Optional[list] = Field(
        None,
        description="A list of Clone options that can be provided multiple "
        "times. One option per list item which is passed exactly as "
        "specified to clone. For example "
        "[‘–config core.filemode=false’, ‘–config core.ignorecase’, "
        "‘–recurse-submodule=repo1_path’, "
        "‘–recurse-submodule=repo2_path’]",
    )
    kwargs: Optional[dict] = Field(
        {},
        description="- odbt = ObjectDatabase Type, allowing to determine the "
        "object database implementation used by the returned Repo "
        "instance "
        "- All remaining keyword arguments are given to the git-clone "
        "command",
    )

    args: list = ['url', 'to_path']

    def exec(self):
        if not self.to_path:
            self.to_path = self.url.split('/')[-1].split('.')[0]
        if self.url:
            Repo.clone_from(
                url=self.url,
                to_path=self.to_path,
                progress=self.progress,
                env=self.env,
                multi_options=self.multi_options,
                **self.kwargs,
            )
            return self.to_path
