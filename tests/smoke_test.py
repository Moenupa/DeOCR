import importlib
import importlib.util

try:
    import pytest
except ImportError:
    pytest: None = None

"""
src
`-- deocr
    |-- __init__.py
    |-- __pycache__
    |   |-- __init__.cpython-312.pyc
    |   `-- load.cpython-312.pyc
    |-- cli.py
    |-- engine
    |   |-- __pycache__
    |   |   |-- args.cpython-312.pyc
    |   |   |-- dataio.cpython-312.pyc
    |   |   `-- defaults.cpython-312.pyc
    |   |-- args.py
    |   |-- dataio.py
    |   |-- defaults.py
    |   |-- playwright
    |   |   |-- __pycache__
    |   |   |   |-- async_api.cpython-312.pyc
    |   |   |   |-- md2html.cpython-312.pyc
    |   |   |   |-- pdf2image.cpython-312.pyc
    |   |   |   `-- sync_api.cpython-312.pyc
    |   |   |-- async_api.py
    |   |   |-- md2html.py
    |   |   |-- pdf2image.py
    |   |   `-- sync_api.py
    |   `-- reportlab
    |       `-- sync_api.py
    `-- load.py
"""


def parametrize(test_func, params):
    """Custom parametrize implementation."""
    for param in params:
        if isinstance(param, tuple):
            test_func(*param)
        else:
            test_func(param)


MODULES = [
    "deocr",
    "deocr.engine",
    "deocr.engine.args",
    "deocr.engine.dataio",
    "deocr.engine.defaults",
    "deocr.engine.playwright.md2html",
    "deocr.engine.playwright.pdf2image",
]


def import_all_modules(module_name: str):
    """Hard-coded import check for every module/submodule."""
    spec = importlib.util.find_spec(module_name)
    assert spec is not None, f"Module spec not found: {module_name}"
    module = importlib.import_module(module_name)
    assert module is not None
    assert getattr(module, "__name__", None) == module_name


if pytest is not None:

    @pytest.mark.parametrize("module_name", MODULES)
    def test_import_all_modules(module_name: str):
        import_all_modules(module_name)


if __name__ == "__main__":
    if pytest is not None:
        pytest.main()
    else:
        parametrize(import_all_modules, MODULES)
