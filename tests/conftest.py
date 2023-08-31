"""Global fixtures for pytest.

Note, each level of tests supports a .env file. The root .env file is
loaded first. Others are loaded within each suite appropriately. Each
test file can also have a .env files as long as the name of the file
is the same as the test file with a .env extension. For example, if
the test file is named test_foo.py, then the .env file should be named
test_foo.env. The .env file is loaded automatically by the
module_env_vars fixture.
"""
import pytest

# Integration with robocorp-log provided by robocorp-log-pytest
from robocorp import log
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent / ".env"
"""Path to the root .env file."""


@pytest.fixture(scope="session", autouse=True)
def root_env_vars() -> None:
    """Loads the .env file associated with the test session."""
    log.info(f"Loading environment variables from {ENV_PATH.name}")
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)


@pytest.fixture(scope="package", autouse=True)
def package_env_vars(request: pytest.FixtureRequest) -> None:
    """Loads the .env files associated with the test package. This would
    be the .env in the root of the test folder, if there is one.
    """
    env_path = request.path.parent / ".env"
    if env_path.exists() and not env_path.samefile(ENV_PATH.parent):
        log.info(f"Loading environment variables from {env_path.name}")
        load_dotenv(env_path)


@pytest.fixture(scope="module", autouse=True)
def module_env_vars(request: pytest.FixtureRequest) -> None:
    """Loads the .env file associated with the current test module. This
    file must be in the same directory as the test module and have the
    same name as the test module with a .env extension.
    """
    env_path = request.path.with_suffix(".env")
    log.info(f"Loading environment variables from {env_path.name}")
    if env_path.exists():
        load_dotenv(env_path)
