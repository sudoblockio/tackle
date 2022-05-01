from tackle import BaseHook
from datetime import datetime


class DateHook(BaseHook):
    """Hook to return the datetime right now."""

    hook_type: str = 'date_now'

    def exec(self):
        return datetime.now()
