# {{ type }}

{{ description }}

## Inputs

| Name | Type | Default | Required | Description |
| :--- | :---: | :---: | :---: | :--- |
{% for i in properties %}| {{ i['name'] }} | {{ i['type'] }} | {{ i['default'] }} | {{ i['required'] }} | {{ i['description'] }} |
{% endfor %}

## Output

