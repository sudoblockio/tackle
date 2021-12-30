"""Web hooks."""
import logging
import webbrowser
from pydantic import AnyUrl, Field

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class WebBrowserHook(BaseHook):
    """Hook for registering a variable based on an input. Useful with rendering."""

    hook_type: str = 'webbrowser'
    url: AnyUrl = Field(..., description="String url to open in browser.")

    def execute(self):
        webbrowser.open(self.url, new=2)
