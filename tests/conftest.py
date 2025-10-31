import pytest
import argparse


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--cleanup",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable cleanup of generated files (default: True). Tests can opt-out with @pytest.mark.nocleanup",
    )


def pytest_configure(config: pytest.Config):
    # register marker so pytest doesn't warn
    config.addinivalue_line(
        "markers", "nocleanup: mark test to disable cleanup of generated files"
    )


@pytest.fixture
def cleanup(request: pytest.FixtureRequest, pytestconfig: pytest.Config) -> bool:
    """
    Returns True when cleanup should run (default), False when cleanup should be skipped.
    Decision order:
      - If CLI --cleanup is set to False (e.g. --no-cleanup) -> skip cleanup (False)
      - If test is marked with @pytest.mark.nocleanup -> skip cleanup (False)
      - Otherwise -> perform cleanup (True)
    """
    cli_cleanup = pytestconfig.getoption("cleanup")
    marker = request.node.get_closest_marker("nocleanup")
    return bool(cli_cleanup) and (marker is None)
