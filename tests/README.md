### Testing Standards

- Directories of the tests should mirror the layout of the project
- Name of the test should reflect the directory the test is in
  - ie:
    - File: `tests/utils/test_paths.py`
    - Test name: `def test_utils_paths_<some description of the test>:`
- All tests are automatically run in the directory of the testing file via a auto-used fixture so that testing from the file + testing via make / tox resolves to the same directory  
- Use the appropriate fixtures to further change directory
  - cd('some-path') -> changes directory
  - cd_fixtures -> changes directory to the fixtures directory
- Common fixtures to a test go in fixtures directory. Fixtures related to a specific set of tests should be nested into their own directory along with the tests file
- Common fixtures to all tests (ie `cd(...)`) live in the `conftest.py` file at the base so that they can be used in the `providers` and `third_party` directories

##### TODO

- Mark tests that install requirements as `slow` and skip them by default
  - Running `make test` should be as fast as possible
  - Running `make test-all` should go through the tests with installs and are therefor slow
- Cleanup old tests
  - `models`
    - These are mostly outdated
  - `main`
    - These are generally redundant and should be RMed
  - `cli`
    - Also many overlaps with tests - should only path specific routes into main logic  

### Testing Current State

Many of these tests are duplicated and need to be cleaned up.
