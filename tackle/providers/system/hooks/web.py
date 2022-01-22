"""Web hooks."""
import webbrowser

from tackle.models import BaseHook, Field


class WebBrowserHook(BaseHook):
    """Hook for registering a variable based on an input. Useful with rendering."""

    hook_type: str = 'webbrowser'
    url: str = Field(..., description="String url to open in browser.")

    _args = ['url']

    def execute(self):
        webbrowser.open(self.url, new=2)
