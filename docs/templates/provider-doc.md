# {{ name }}
{% if description is defined %}
{{ description }}{% endif %}

### Hooks  

| Type | Description | Return |
| :--- | :--- | :--- |{% for i in hooks %}
| [{{ i.hook_type }}]({{ i.hook_type }}.md) | {{ i.description }} | | {% endfor %}
{% if requirements != [] %}
### Requirements

| Requirement |  
| :--- | {% for i in requirements %}
| {{ i }} | {% endfor %}

{% endif %} {% if examples is defined %}
### Examples

{% for i in examples %}
#### {{ i.name }}

{{ i.description }}

```yaml
{{ i.content }}
```
{% endfor %}
{% endif %}

