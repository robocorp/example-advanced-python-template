"""Common shared code for tasks."""
import os
from pathlib import Path

from robocorp import storage, log

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
