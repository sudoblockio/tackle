# {{ name }}

{{ if description }}
{{ description }}
{{ endif }}

## Hooks  

| Type | Description | Return |
| :--- | :--- | :--- | :--- | :--- |
{{ for i in inputs }}
| {{ i.name }} | {{ i.required }} | {{ i.type }} | {{ i.default }} | {{ i.description }} |
{{ endfor }}


{{ if requirements }}

## Requirements

{{ endif }}


