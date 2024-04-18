.DEFAULT_GOAL := help

VENV_NAME?=".venv"
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=${VENV_NAME}/bin/python3

.PHONY: all
all: venv

venv: $(VENV_NAME)/bin/activate
	$(VENV_NAME)/bin/activate: requirements.txt
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -r requirements.txt
	touch $(VENV_NAME)/bin/activate

.PHONY: clean
clean:
	rm -rf $(VENV_NAME)

.PHONY: run
run:
	$(VENV_ACTIVATE) && python3 my_script.py


install:  ## Install all the requirements
	@echo "+ $@"
	@pip install -e .\[all\] -r requirements-dev.txt -r docs/requirements.txt

.PHONY: clean-tox
clean-tox: ## Remove tox testing artifacts
	@echo "+ $@"
	@rm -rf .tox/

.PHONY: clean-build
clean-build: ## Remove build artifacts
	@echo "+ $@"
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

.PHONY: clean-pyc
clean-pyc: ## Remove Python file artifacts
	@echo "+ $@"
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '*.py[co]' -exec rm -f {} +
#	@find . -name '*~' -exec rm -f {} +

.PHONY: clean
clean: clean-tox clean-build clean-pyc ## Remove all file artifacts

.PHONY: lint
lint: ## Check code style with flake8
	@echo "+ $@"
	@tox -e lint

.PHONY: test
test:  clean-pyc  ## Run tests quickly with the default Python
	@echo "+ $@"
	@tox -e py -- --skip-slow

.PHONY: test-all
test-all:  clean-pyc  ## Run all tests including the slow ones with the default Python
	@echo "+ $@"
	@tox -e py

.PHONY: test-all-python-versions
test-all-python-versions: ## Run tests on every Python version with tox
	@echo "+ $@"
	@tox

.PHONY: test-providers
test-providers: ## Run tests on every Python version with tox
	@echo "+ $@"
	@tox -e providers

.PHONY: coverage
coverage: ## Check code coverage quickly with the default Python
	@echo "+ $@"
	@tox -e cov-report
	@$(BROWSER) htmlcov/index.html

provider-docs: ## Generate Sphinx HTML documentation, including API docs
	@tackle docs_gen

.PHONY: docs
docs: provider-docs ## Generate Sphinx HTML documentation, including API docs
	@echo "+ $@"
	@mkdocs build

.PHONY: servedocs
servedocs: docs ## Rebuild docs automatically
	@echo "+ $@"
	@mkdocs serve

.PHONY: release
release: clean ## Package and upload release
	@echo "+ $@"
	@python setup.py sdist bdist_wheel
	@twine upload -r pypitest dist/*

.PHONY: sdist
sdist: clean ## Build sdist distribution
	@echo "+ $@"
	@python setup.py sdist
	@ls -l dist

.PHONY: wheel
wheel: clean ## Build bdist_wheel distribution
	@echo "+ $@"
	@python setup.py bdist_wheel
	@ls -l dist

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
