{{ fullname | escape | underline }}

.. automodule:: {{ fullname }}

{% block classes %}
{% if classes %}
.. rubric:: Classes

.. autosummary::
   :toctree:
   :template: autosummary/class.rst
   :nosignatures:

{% for item in classes %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

{% block functions %}
{% if functions %}
.. rubric:: Functions

.. autosummary::
   :toctree:
   :nosignatures:

{% for item in functions %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

{% block attributes %}
{% if attributes %}
.. rubric:: Module attributes

{% for item in attributes %}
.. autodata:: {{ item }}
   :no-value:
{%- endfor %}
{% endif %}
{% endblock %}
