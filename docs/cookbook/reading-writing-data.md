# Reading and Writing Data

### The `yaml` / `json` / `toml` hooks

Each of these hooks allow reading and writing to files in essentially same way.

To read from a file:

```yaml
vars->: yaml some-file.yaml
```

To write to a file:

```yaml
some:
  important: data

compact->: yaml some-file.yaml {{some}}
expanded:
  ->: yaml
  path: some-file.yaml
  data:
    important: data
```

### The `yaml_in_place` / `json_in_place` / `toml_in_place` hooks

Yaml / json / toml can be updated in place, ie without having to both read and write the file over consecutive hook calls.

**Docs**

- [`yaml_in_place`][../providers/Yaml/yaml_in_place.md]
- [`json_in_place`][../providers/Json/json_in_place.md]
- [`toml_in_place`][../providers/Toml/toml_in_place.md]

> NOTE: These are still a WIP