"""This module shows an example of providing for repository-wide
specific errors, which help in detecting and releasing errors
within individual work items back to the Control Room.
"""


class AutomationError(Exception):
    """Base class for all automation errors."""
