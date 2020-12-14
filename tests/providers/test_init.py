import os
from tackle.models import Settings
import pytest
from tackle.main import tackle


@pytest.mark.parametrize("input_fixture", ("template-working", "that"))
def test_import_fixture(tmpdir, change_dir, input_fixture):
    input_fixture = os.path.join('fixtures', input_fixture)
    o = tackle(input_fixture, no_input=True, output_dir=str(tmpdir), rerun=True,)


def test_import_local_providers():
    s = Settings(extra_provider_dirs=["~/"])
    print()
