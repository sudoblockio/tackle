import datetime
from datetime import timezone

from tackle import BaseHook, Field


class DateTimeNowHook(BaseHook):
    """Hook for updating dict objects with items."""

    hook_type: str = 'date_now'
    format: str = Field(
        "%m-%d-%Y",
        description="Date time formatting per [the official docs](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior)",
    )

    timestamp: bool = Field(
        False, description="Output as timestamp. Precedence over format."
    )
    utc: bool = Field(False, description="Output in UTC.")

    args: list = ['format']

    def exec(self) -> str:

        if self.timestamp:
            if self.utc:
                dt = datetime.datetime.now(timezone.utc)
                utc_time = dt.replace(tzinfo=timezone.utc)
                now = utc_time.timestamp()
            else:
                now = datetime.datetime.now().timestamp()
        else:
            if self.utc:
                now = datetime.datetime.utcnow().strftime(f'{self.format}')
            else:
                now = datetime.datetime.now().strftime(f'{self.format}')
        return now
