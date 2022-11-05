import re
from typing import List

from tackle import BaseHook, Field


class UpdateSectionHook(BaseHook):
    """Hook for updating a section of a document."""

    hook_type: str = 'update_section'
    document: str = Field(..., description="Path to a document to render a section of.")
    content: str = Field(
        ..., description="A string to update within the section of the document"
    )
    start_render: str = Field(
        '--start--',
        description="Marker generally in some kind of comment to begin rendering from.",
    )
    end_render: str = Field(
        '--end--',
        description="Marker generally in some kind of comment to end rendering from.",
    )

    args: list = ['document', 'content']

    def split_document(self, doc: List[str]) -> str:
        upper_section = []
        lower_section = []
        in_section = False
        in_upper = True

        for line in doc:
            if re.search(self.start_render, line):
                upper_section.append(line)
                in_section = True
            if re.search(self.end_render, line):
                lower_section.append(line)
                in_section = False
                in_upper = False
            elif not in_section:
                if in_upper:
                    upper_section.append(line)
                else:
                    lower_section.append(line)

        upper_str = "".join(upper_section)
        lower_str = "".join(lower_section)

        return "\n".join([upper_str, self.content, lower_str])

    def exec(self):
        with open(self.document) as f:
            doc = f.readlines()

        output = self.split_document(doc)

        with open(self.document, 'w') as f:
            f.write(output)
