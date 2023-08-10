"""Unit tests for the Swag Labs automation class"""

import pytest

from robocorp import browser

# System under test
from web import swaglabs


def test_browser():
    browser1 = browser.browser()
    swag = swaglabs.Swaglabs()
    swag.configure()
    browser2 = swag._browser
    assert browser1 is browser2
