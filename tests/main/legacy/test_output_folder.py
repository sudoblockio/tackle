"""
tests_output_folder.

Test formerly known from a unittest residing in test_generate.py named
TestOutputFolder.test_output_folder
"""
import os

import pytest

from tackle.utils import paths
from tackle import exceptions
from tackle import generate
from tackle.main import tackle


@pytest.fixture(scope='function')
def remove_output_folder(change_dir_main_fixtures, request):
    """Remove the output folder after test."""
    yield
    if os.path.exists('output_folder'):
        paths.rmtree('output_folder')


@pytest.mark.usefixtures('clean_system', 'remove_output_folder')
def test_output_folder(change_dir_main_fixtures):
    """Tests should correctly create content, as output_folder does not yet exist."""
    tackle('test-output-folder', no_input=True)

    something = """Hi!
My name is Audrey Greenfeld.
It is 2014."""
    something2 = open('output_folder/something.txt').read()
    assert something == something2

    in_folder = "The color is green and the letter is D."
    in_folder2 = open('output_folder/folder/in_folder.txt').read()
    assert in_folder == in_folder2

    assert os.path.isdir('output_folder/im_a.dir')
    assert os.path.isfile('output_folder/im_a.dir/im_a.file.py')


@pytest.mark.usefixtures('clean_system', 'remove_output_folder')
def test_exception_when_output_folder_exists(change_dir_main_fixtures):
    """Tests should raise error as output folder created before `generate_files`."""
    if not os.path.exists('output_folder'):
        os.makedirs('output_folder')
    with pytest.raises(exceptions.OutputDirExistsException):
        tackle('test-output-folder', no_input=True)
