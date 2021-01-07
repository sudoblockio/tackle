.. _new-lines:

Working with line-ends special symbols LF/CRLF
----------------------------------------------

By default Tackle Box checks every file at render stage and uses same line
endings as in source. This allow template developers to have both types of files in
the same template. Developers should correctly configure their `.gitattributes`
file to avoid line-end character overwrite by git.

Special template variable `_new_lines` is available
Acceptable variables: `'\n\r'` for CRLF and `'\n'` for POSIX.

Here is example how to force line endings to CRLF on any deployment::

    {
        "project_slug": "sample",
        "_new_lines": "\n\r"
    }
