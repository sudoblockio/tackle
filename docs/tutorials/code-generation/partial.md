# Partial Code Generating Techniques

Several strategies can be used to partially update a tackle file.

### Rendering Segments Ahead of Time

Segments of a code generation can be done ahead of time.

```yaml
python_function_template: |
  {%for i in foo%}
  def {{i}}Function(x: int, y: int)
    print(x + y)
  {% endfor%}

python_function_rendered->: {{python_function_template}}
```

Which can then be further combined within the tackle file, rendered into a template, or updated within a file as described below.

### Generating a File Once

Within the [generate](../../providers/Generate/generate.md) hook, there is an option to `skip_if_file_exists` which can mark certain files as non-renderable if they are code generated and expected to change after the code generation. This way the files are only generated once and skipped if they exist.

### Updating a Section

Using the [`update_section`](../../providers/Generate/update_section.md) hook, you can set markers in a document to pass over rendering to. For instance lets say you wanted to hand control over to tackle for updating a table in the document. Once could do:

**`.tackle.yaml`**
```yaml
update_readme<-:
  help: Update the README.md table
  exec:
    rows:
      - name: Stuff
        desc: A thing
      - name: Thing
        desc: A stuff
    update:
      ->: update_section README.md
      content: |
        | Name | Description |
        |---|---|
        {% for i in rows %}| {{i.name}} | {{i.desc}} |
        {% endfor %}
```

Running `tackle update-readme`

```markdown
My App...

[//]: # (--start--)

| Name | Description |
|---|---|
| Stuff | A thing |
| Thing | A stuff |

[//]: # (--end--)

Does stuff
```

You can also update multiple sections by toggling the [`start_render` and `end_render`](../../providers/Generate/update_section.md) fields. It is also up to you how you build the sources which could be in remote locations.
