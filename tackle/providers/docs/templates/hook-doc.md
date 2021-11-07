# {{ type }}

{% if description %}
{{ description }}
{% endif %}

## Inputs

| Name | Type | Default | Required | Description |
| :--- | :---: | :---: | :---: | :--- |
{% for i in properties %}| {{ i['name'] }} | {{ i['type'] }} | {{ i['default'] }} | {{ i['required'] }} | {{ i['description'] }} |
{% endfor %}

## Arguments

| Position | Argument | Type |
| :--- | :---: | :---: |
{% for i in arguments %}| {{ loop.index }} | {{ i['argument'] }} | {{ i['type'] }} |
{% endfor %}



## Output

{{ description }}
