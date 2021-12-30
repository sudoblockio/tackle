# {{ type }}

{{ description }}

## Inputs

| Name | Required | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
{% for i in properties %}
| {{ i['name'] }} | {{ i['required'] }} | {{ i['type'] }} | {{ i['default'] }} | {{ i['description'] }} |
{% endfor %}

