# Templating with Tackle

```shell
tackle help 
#usage: tackle   
#
#methods:
#    gen_file     Generate a file with tackle
#    gen_dir      Generate a directory of templates with tackle
#    gen_readme   Update a section in a readme with tackle
tackle gen_file 
tackle gen_dir 
tackle gen_readme
```

### tackle file 

> Below code is inserted into this file with tackle by running `tackle gen_readme`

[//]: # (--start--)


```yaml
gen_file(help str = "Generate a file with tackle")<-:
  ->: generate a_file.py.j2 output/a_file.py
  extra_context:
    foo: bar


gen_dir(help str = "Generate a directory of templates with tackle")<-:
  ->: generate a_dir output/another_dir
  extra_context:
    foo: "{{ input() }}"

gen_readme(help str = "Update a section in a readme with tackle")<-:
  ->: update_section README.md
  content: |
    
    ```yaml
    {{ file('tackle.yaml') }}
    ```
```
[//]: # (--end--)
