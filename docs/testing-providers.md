# Testing Providers

- Testing hooks
- Testing tackle files
  - Overrides




```python
def test_collections_hook_concate(change_dir):
    output = tackle('concatenate.yaml')
    assert output['out'] == ['foo', 'bar', 'stuff', 'things']
```
