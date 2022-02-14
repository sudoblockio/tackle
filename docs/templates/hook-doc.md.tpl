# {{ hook_type }}
[Source]({{ source_code_link_stub }}/{{ hook_file_name }})
{#Description#}
{% if description %}
{{ description }}
{% endif %}
{#Notes#}
{% if notes|length > 0 %}
{% for i in notes %}
> {{ i }}
{% endfor %}
{% endif %}
{#Status#}
{% if 'experimental' in doc_tags %}
> Warning: Hook is experimental. Expect changes.
{% endif %}
{% if 'wip' in doc_tags %}
> Warning: Hook is a work in progress. Expect changes.
{% endif %}
{#Inputs#}
## Inputs
{% if properties|length > 0 %}
| Name | Type | Default | Required | Description |
| :--- | :---: |:---:| :---: | :--- |
{% for i in properties %}| {{ i['name'] }} | {{ i['type'] }} | {{ i['default'] }} | {{ i['required'] }} | {{ i['description'] }} |
{% endfor %}{% else %}No inputs{% endif %}
{#Arguments#}
{% if arguments|length > 0 %}
## Arguments
| Position | Argument | Type |
|:---| :---: | :---: |
 {% for i in arguments %} | {{ loop.index }} | {{ i['argument'] }} | {{ i['type'] }} |
{% endfor %}{% endif %}
{#Output#}
## Returns
`{{ return_type }}`{% if return_description %} - {{ return_description }}{% endif %}
{% if hook_examples is defined %}{% if hook_type in hook_examples %}
{#Examples#}
## Examples
{% for i in hook_examples[hook_type] %}{% if i.name is defined %}
### {{ i.name }}{% endif %}{% if i.description is defined %}
{{ i.description }}{% endif %}
```yaml
{{ i.content }}
```{% if i.output_text is defined %}
{{ i.output_text }}{% endif %}
{% if i.output is defined %}
```yaml
{{i.output}}
```{% endif %}
{% endfor %} {% endif %} {% endif %}
{#Issues#}
{% if issue_numbers|length > 0 %}
> Warning: Tracking issues relating to this hook
    {% for i in issue_numbers %}
        - [{{ i }}](https://github.com/robcxyz/tackle-box/issues/{{ i }})
    {% endfor %}
{% endif %}
