"""Common shared code for tasks."""
import os
import json
from pathlib import Path

from robocorp import vault, storage, log

ARTIFACTS_DIR = os.getenv("ROBOT_ARTIFACTS", "output")
ROBOT_ROOT = Path(__file__).parent.parent
DEVDATA = ROBOT_ROOT / "devdata"


def _setup_log() -> None:
    """Tries to use the LOG_LEVEL text asset or environment variable
    to set the log level. If the value is not valid, the default is
    "info". The environment variable will override the asset value.
    """
    try:
        log_level = storage.get_text("LOG_LEVEL")
    except (storage.AssetNotFound, RuntimeError, KeyError):
        log_level = "info"
    log_level = os.getenv("LOG_LEVEL", log_level)
    try:
        log_level = log.FilterLogLevel(log_level)
    except ValueError:
        log_level = log.FilterLogLevel.INFO
    log.setup_log(output_log_level=log_level)


def _get_secret(system: str) -> vault.SecretContainer:
    """Gets the appropriate secret from the vault based on
    the system name and the mapping within the Control Room
    asset storage. This is a simple example of how you can
    use the asset storage system to configure your bots.

    In this example, the mapping should be stored in the asset storage
    as a JSON object named "system_credential_index" with the following
    structure:
        {
            "system_name": "secret_name",
            ...
        }

    For the sake of this example, this function loads a mapping from
    a file named "system_credential_index.json" in the devdata directory,
    but if you are using the Control Room, you can create this asset
    in your Workspace and it will use that instead.
    """
    try:
        mapping = storage.get_json("system_credential_index")
    except (storage.AssetNotFound, RuntimeError, KeyError):
        # If the asset is not found, use the local file instead.
        with (DEVDATA / "system_credential_index.json").open() as file:
            mapping = json.load(file)
    try:
        assert isinstance(mapping, dict)
        secret_name = mapping[system]
    except KeyError:
        raise KeyError(f"System {system} not found in mapping.")
    except (TypeError, AssertionError):
        raise TypeError("Mapping is not a dictionary-like JSON object.")
    assert isinstance(secret_name, str)
    return vault.get_secret(secret_name)


__all__ = ["ARTIFACTS_DIR", "ROBOT_ROOT", "DEVDATA", "_setup_log", "_get_secret"]
