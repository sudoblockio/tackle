# Base Methods

Besides fields associated with flow control like `if`, `else`, `when`, and `for`, we also have access to a number of other base methods:

- `try` / `except` -> Catch errors and do something
- `merge` -> Move the output up one level or append to the parent list
- `chdir` -> Change directory for a hook execution

### `try` / `except`

```yaml
a failed command->: command "foo bar" --try  # Would exit without try
p->: print Hello world!  # This would print
```

```yaml
a failed command:
  ->: command "foo bar"
  try: true
  except:
    p->: print Hello world!
```

Values can also be renderable strings.

### `merge`

When using the `merge` key, the output of the hook is merged up one level for objects and appended for lists.

**Objects**  

```yaml
stuff: things

merge an object->:
  merge: true
  stuff: more things
```

Results in:

```yaml
stuff: more things
```

**Lists**  

```yaml
- stuff: things
- merge a list->:
    merge: true
    stuff: more things
```

Results in:

```yaml
- stuff: things
- stuff: more things
```

### `chdir`

A hook can be temporarily executed in a directory

```yaml
call->: file some-file --chdir path/to/file
```