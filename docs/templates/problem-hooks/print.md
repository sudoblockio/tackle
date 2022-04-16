# print
[Source](https://github.com/robcxyz/tackle-box/blob/main/tackle/providers/console/hooks/prints.py)

Hook for printing an input and returning the output. [Link](https://docs.python.org/3/library/functions.html#print)

## Inputs

| Name | Type | Default | Required | Description |
| :--- | :---: |:-------:| :---: | :--- |
| objects | any |  None   | False | The objects to print. |
| sep | str |  | False | Separator between printed objects. |
| end | str |  '\n'  | False | What to print at the end |
| flush | bool |  False  | False | No clue. |

## Arguments
| Position | Argument | Type |
|:---| :---: | :---: |
  | 1 | objects | any |

## Returns
`NoneType`

## Examples

### Compact print - most common use
```yaml
compact->: print stuff and things
```

### Expanded print
```yaml
expanded:
  ->: print
  objects: stuff and
  end: " "
```
Output:
```text
stuff and things
```




