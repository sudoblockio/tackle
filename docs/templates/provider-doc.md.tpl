# {{ name }}
{% if description is defined %}
{{ description }}{% endif %}

{% if note is defined %}
> {{ note }}{% endif %}


### Hooks

| Type | Description | Return |
| :--- | :--- | :--- |{% for i in hooks %}
| [{{ i.hook_type }}]({{ i.hook_type }}.md) | {{ i.description }} | {{ i.return_type }} | {% endfor %}

{% if requirements != [] %}
### Requirements
{% for i in requirements %}
- {{ i }}{% endfor %}{% endif %}


{% if examples is defined %}
### Examples

{% for i in examples %}
#### {{ i.name }}{% if i.description is defined %}
{{ i.description }}{% endif %}

```yaml
{{ i.content }}
```{% if i.output_text is defined %}
{{ i.output_text }}{% endif %}{% if i.output is defined %}
```yaml
{{i.output}}
```{% endif %}{% endfor %}{% endif %}