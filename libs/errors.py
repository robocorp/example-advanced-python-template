"""This module shows an example of providing for repository-wide
specific errors, which help in detecting and releasing errors
within individual work items back to the Control Room.

These errors derive from the ApplicationException and BusinessException
classes, which are provided by the robocorp.workitems module. When raised
from a work item, they are automatically detected and released back to
the Control Room as the appropriate error type, therefore manually
releasing work items is not required within robot code.

For exceptions that are not derived from ApplicationException or
BusinessException, the work item will automatically release as an
Application error.
"""
from robocorp.workitems import ApplicationException, BusinessException


class AutomationError(Exception):
    """Base class for all automation errors. This base class
    allows for catching all automation errors, regardless of
    whether they are application or business errors.
    """


class ApplicationError(AutomationError, ApplicationException):
    """Base class for all application errors. Application errors
    are errors that are usually transient. A work item being
    processed when such an error occurs can be retried.
    """


class BusinessError(AutomationError, BusinessException):
    """Base class for all business errors. Business errors are
    errors that are usually permanent. A work item being
    processed when such an error occurs should not be retried
    and likely needs to be corrected.
    """
