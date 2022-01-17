{{ name }}
===============

API Reference
-------------

.. toctree::
   :maxdepth: 2

   {% for i in hooks %}
   {{ i.hook_type }} {% endfor %}

Index
-----

* :ref:`genindex`
* :ref:`modindex`