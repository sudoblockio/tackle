"""Allow cookiecutter to be executable from a checkout or zip file."""
import runpy


if __name__ == "__main__":
    runpy.run_module("tackle", run_name="__main__")
