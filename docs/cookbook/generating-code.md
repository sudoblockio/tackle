# Code Generating Examples

Please checkout the [](../tutorials/code-generation/index.md) docs for more thorough examples.

### Simple generation example

```yaml
# Render context
foo: bar

# Call generate hook
generate hook in compact form->: generate path/to/templates output/path
# Or
generate hook in expanded form:
  ->: generate
  templates: path/to/templates
  output: output/path
```

### Sample Project Structure

For instance given this file structure:

```
├── templates
│ └── file1.py
│ └── file2.py
│ └──── dir
└── tackle.yaml
```

**`tackle.yaml`**
```yaml
project_name->: input
project_slug->: input --default "{{project_name.lower()|replace(' ', '_')|replace('-', '_')|replace('.', '_')|trim()}}"
github_username->: input What is your Github username / org?
license->: select --choices ['apache','mit']
# or use the license hook
#license->: tackle robcxyz/tackle-license --output {{project_slug}}
postgres_version:
  ->: select
  choices:
    - 14
    - 13
    - 12
gen code->: generate templates {{project_slug}}
```

Would generate the following structure:

```
│ └── file1.py
│ └── file2.py
│ └──── dir
└── LICENSE
```

### Using Remote Providers

Here is an example of how to use a license hook.

```yaml
# project_slug is a standard name for your package directory
project_slug->: input What to call the project?
license->: tackle robcxyz/tackle-license --output {{project_slug}}
# project_slug is again used for other rendering outputs
```

### Flow Control

```yaml
use_docker->: confirm Do you want to use docker?
docker->:
  if: use_docker
  os:
    ->: select What docker base image?
    choices:
      - ubuntu
      - alpine
      - centos
  registry->: select Where to push docker image? --choices ['dockerhub','quay']
  generate dockerfile->: generate templates/Dockerfile {{project_slug}}/Dockerfile

# Use items inside block to render other templates
# For instance one could use {{docker.registry}} in a template
generate ci->: generate templates/.github {{project_slug}}
```

Another version of the same without a `use_docker` variable:

```yaml
docker->:
  if: confirm('Do you want to use docker?')
  os->: select What docker base image? --choices ['ubuntu','alpine','centos']
  registry->: select Where to push docker image? --choices ['dockerhub','quay']
  generate dockerfile->: generate templates/Dockerfile {{project_slug}}/Dockerfile
generate ci->: generate templates/.github {{project_slug}}
```

### Splitting up Context

Not specifically to code generation, but it is sometimes useful to have a sort of hierarchical layout with global variables. For instance:

**`child/tackle.yaml`**
```yaml
context: tackle global.yaml --find_in_parent --merge
```

**`global.yaml`**

```yaml
envs_>:
  dev:
    num_servers: 1 # etc...
  prod:
    num_servers: 2

# or in multiple lines / mix
environments:
  - prod
  - dev
env->: select --choices environments
merge it up a level with var hook->: var envs[env] --merge

Or all the above in one line->: var {{envs[select(choices=keys(envs))]}} --merge
```

Resulting in the following context

```yaml
#? env >>> prod
environments:
- prod
- dev
env: prod
num_servers: 2
```

And then can be used to generate code or call CLIs wrapped with tackle such as kubectl.

### Rendering in Segments

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


### Using the [update_section](../providers/Generate/update_section.md) Hook

Tackle can be used to update a section between two markers.

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
