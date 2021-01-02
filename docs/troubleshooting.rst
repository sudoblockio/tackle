===============
Troubleshooting
===============

Troubleshooting Tackle Files
----------------------------

Often times you find yourself debugging a script and have to enter the same options over and over again which is annoying and difficult to deal with when dealing with many options. For that, it is recommended to use the `record` and `rerun` functionality

Troubleshooting Jinja templates
-------------------------------

Make sure you escape things properly, like this::

    {{ "{{" }}

Or this::

    {% raw %}
    <p>Go <a href="{{ url_for('home') }}">Home</a></p>
    {% endraw %}

Or this::

    {{ {{ url_for('home') }} }}

See http://jinja.pocoo.org/docs/templates/#escaping for more info.

You can also use the `_copy_without_render`_ key in your `tackle.yaml`
file to escape entire files and directories.

.. _`_copy_without_render`: http://cookiecutter.readthedocs.io/en/latest/advanced/copy_without_render.html


Other common issues
-------------------

TODO: add a bunch of common new user issues here.

This document is incomplete. If you have knowledge that could help other users,
adding a section or filing an issue with details would be greatly appreciated.
