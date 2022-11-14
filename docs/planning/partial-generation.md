
# Partial Code Generation

> Note this has been side stepped in favor of the update_section hook

- Different types of partial generation
  - Template render on/off directives
    - Can be interpreted in different ways
      1. As a sort of jinja `raw`/`end_raw` directive
        - This already exists
      2. As something to inform initial vs secondary renders
        - If the file does not exist, then render all sections
        - If the file exists, then only render the designated sections
          - ISSUE is that we add a section and will lose order
            - This is assuming you slice up a document and render them individually
              - What is to say if the original added the directive vs the template
      3. As something that informs ownership over a certain part of the doc
        -


  - Generate can be responsible for a single section
    - Markers defined in generate statement

- Need to be able to render only part of the document
  - Similar to having a section of a document being renderable



### Examples

```python
not_rendered = "{{ foo }}"
# --START--
rendered = "{{ foo }}"
# --END--
not_rendered2 = "{{ foo }}"
```

```python
rendered = "{{ foo }}"
# --END--
not_rendered = "{{ foo }}"
```



```python
rendered = "{{ foo }}"
# --END--
not_rendered = "{{ foo }}"
# --START--
rendered2 = "{{ foo }}"
```

### Implementation



#### Example Implementation

[source](https://www.geeksforgeeks.org/how-to-split-a-file-into-a-list-in-python/#:~:text=Example%201%3A%20Using%20the%20splitlines()&text=Here%20as%20we're%20reading,using%20the%20close()%20method.****)
```python
document_slices = []  # A list of strings to indicate the parts of the document
marker_indexes: list[bool] = []  # List of bools to indicate rendering

start_marker = "--START--"
end_marker = "--END--"
markers = (start_marker, end_marker)

with open("file.txt", 'r') as file_data:
    section_number = 0
    for line in file_data:
        if start_marker in line:
            marker_indexes.append(False)  # Wrong
            section_number += 1
        data = line.split()
        print(data)
```