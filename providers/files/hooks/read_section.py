import re

from tackle import BaseHook, Field


class UpdateSectionHook(BaseHook):
    """Hook for reading a section of a document."""

    hook_name = 'read_section'
    document: str = Field(..., description="Path to a document to render a section of.")
    start: str = Field(
        '--start--',
        description="Marker generally in some kind of comment to begin reading from.",
    )
    end: str = Field(
        '--end--',
        description="Marker generally in some kind of comment to end reading from.",
    )

    args: list = ['document', 'start', 'end']

    def exec(self):
        with open(self.document) as f:
            doc = f.readlines()

        section = []
        in_section = False

        for line in doc:
            if re.search(self.start, line):
                in_section = True
            elif re.search(self.end, line):
                in_section = False
            elif in_section:
                section.append(line)

        return "\n".join(section)
