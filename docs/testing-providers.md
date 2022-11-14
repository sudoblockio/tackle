# Testing Providers

- Testing hooks
- Testing tackle files
  - Overrides

Being able to test both the tackle files and providers is critical to building maintainable tackle files / hooks. Tackle uses pytest and a number of useful fixtures to enable testing. The following outlines some patterns that developers might find useful when testing their own providers.


## Testing Native Hooks

Currently, all native hooks (ie providers that ship with tackle) use this pattern to allow running the tests locally from within the test's directory and from the Makefile with tox. It uses a fixture to change the directory to the test and runs a tackle file using the hook.

**Fixture in `conftest.py`**
```python
import pytest
import os

@pytest.fixture(scope="function")
def change_dir(request):
    """Change to the current directory of the test."""
    os.chdir(request.fspath.dirname)
```

Then uses that fixture in the test like so:

```python
from tackle import tackle

def test_provider_assert(change_dir):
    """Check assertions."""
    output = tackle('hook-fixture.yaml')
    assert output['foo'] == 'bar'
```

The `hook-fixture.yaml` is some file that exercises the hook to demonstrate its functionality whose output can then be asserted.

## Testing the Default Tackle File

When testing providers, often times there will be some tackle file which needs to have various options overriden. The following outlines how you can test tackle files that are built with and without declarative hooks which change the way options need to be overriden.

Each of these tests assumes the test is being run from the base directory. To achieve this, one needs to additional supply a fixture that changes the directory.

```python
import pytest
import os

@pytest.fixture(scope='function')
def change_base_dir(monkeypatch):
    """Change to the base directory for importing hooks."""
    monkeypatch.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
```

### Testing With Declarative Hooks

Declarative hook fields can be supplied via command line or when using tackle's main entrypoint (ie `tackle.main.tackle`), with arguments or kwargs.

**`.tackle.yaml`**
```yaml
a_hook<-:
  option1->: input
  option2->: input
```

**`tests/test_main.py`**

```python
from tackle import tackle

def test_main_build(change_base_dir):
    output = tackle('a_hook', option1='foo', option2='bar')

    assert output['option1'] == 'foo'
```

Notice that both args and kwargs are simply provided in the tackle function. If you need to supply flags, you can do so via kwargs or as a list of

**`.tackle.yaml`**
```yaml
a_hook<-:
  a_flag: bool
```

**`tests/test_main.py`**

```python
from tackle import tackle

def test_main_build(change_base_dir):
    output = tackle('a_hook', a_flag=True, global_flags=['a_flag'])

    assert output['a_flag']
```

### Testing Tackle Scripts

Tackle files don't need to have declarative hooks exposed but need to have values overriden if they require some kind of user input. For instance given this tackle file, you would need to

**`.tackle.yaml`**

```yaml
a_input->: input
# More business logic using `a_input`
```

**`tests/test_main.py`**

```python
from tackle import tackle

def test_main_build(change_base_dir):
    output = tackle(override={'a_input': 'foo'})

    assert output['a_input'] == 'foo'
```

Or as kwargs:
```python
def test_main_build(change_base_dir):
    output = tackle(a_input='foo')
    # assert...
```

Or if you have a file of values you want to override:

**`tests/a-fixture.yaml`**

```yaml
a_input: foo
```

```python
def test_main_build(change_base_dir):
    output = tackle(override='a-fixture.yaml')
    # assert...
```

Which is the logical input from the command line, ie `tackle some-target -o a-fixture.yaml`.
