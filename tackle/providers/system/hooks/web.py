"""Web hooks."""
import logging
import webbrowser
from pydantic import AnyUrl

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class WebBrowserHook(BaseHook):
    """
    Hook  for registering a variable based on an input. Useful with rendering.

    :param url: String url to open in browser.
    :return: None
    """

    type: str = 'webbrowser'
    url: AnyUrl

    def execute(self):
        webbrowser.open(self.url, new=2)
