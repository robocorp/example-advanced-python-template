"""The web package is an example of a sub-package focusing on automating
various web sites. In this repository, there is only one, but in a 
more complex example, you would have potentially many more.

Note: In many Python use cases, all errors are collected in one module,
but in this repo, only general errors are included in the errors modules
and specific errors are defined within each automation module.
"""
from errors import AutomationError


class WebAutomationError(AutomationError):
    """Base class for all web automation errors."""
