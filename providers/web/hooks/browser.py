import webbrowser

from tackle.models import BaseHook, Field


class WebBrowserHook(BaseHook):
    """
    Open a web browser. Wraps python's
     [webbrowser](https://docs.python.org/3/library/webbrowser.html#browser-controller-objects)
     module.
    """

    hook_type: str = 'webbrowser'
    # fmt: off
    url: str = Field(..., description="String url to open in browser.")
    new: int = Field(0, description="If new is 1, a new browser window is opened if possible. If new is 2, a new browser page (“tab”) is opened if possible.")
    autoraise: bool = Field(True, description="If autoraise is True, the window is raised if possible (note that under many window managers this will occur regardless of the setting of this variable).")
    # fmt: on

    args: list = ['url']

    def exec(self):
        webbrowser.open(self.url, new=2)
