# Reading and Writing Data

### The `yaml` / `json` / `toml` hooks

The [yaml](../providers/Yaml/yaml.md), [json](../providers/Json/json.md) hooks allow reading and writing to files in essentially same way. Also see [toml](../providers/Toml/toml.md), [ini](../providers/Ini/ini.md), and [file](../providers/Files/file.md) hooks which are similar.

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

> Note this is a WIP. Input welcome.

Yaml / json / toml can be updated in place, ie without having to both read and write the file over consecutive hook calls.

**Docs**

- [`yaml_in_place`](../providers/Yaml/yaml_in_place.md)
- [`json_in_place`](../providers/Json/json_in_place.md) - WIP

> NOTE: These are still a WIP. Focus is on yaml_in_place and then will be shared by json and toml.