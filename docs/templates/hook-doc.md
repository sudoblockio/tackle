# {{ hook_type }}

{% if description %}
{{ description }}
{% endif %}

## Inputs

| Name | Type | Default | Required | Description |
| :--- | :---: |:---:| :---: | :--- |
{% for i in properties %}| {{ i['name'] }} | {{ i['type'] }} | {{ i['default'] }} | {{ i['required'] }} | {{ i['description'] }} |
{% endfor %}

## Arguments

| Position                 | Argument | Type |
|:-------------------------| :---: | :---: |
 {% for i in arguments %} | {{ loop.index }} | {{ i['argument'] }} | {{ i['type'] }} |
{% endfor %}
{% if output is defined %}
## Output

{{ output }} {% endif %}
{% if hook_examples is defined %}{% if hook_type in hook_examples %}
## Examples
{% for h in hook_examples[hook_type] %}
### {{ h['name'] }}

{{ h['description'] }}

```yaml
{{ h['content'] }}```
{% endfor %} {% endif %} {% endif %}
