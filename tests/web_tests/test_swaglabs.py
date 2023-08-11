"""Unit tests for the Swag Labs automation class

Tests which interact with the Swag Labs website are marked as live.

This module supports an environment variable file with the following
variables:
 * BASE_URL: The base URL of the Swag Labs website, for testing a non-demo
    website, you should set this to the site's test URL.
 * SECRET_NAME: The name of the secret in the CR vault which contains the
    website credentials.
"""
import pytest
from typing import Generator, Union

from robocorp import browser, vault

# System under test
from web.swaglabs import (
    Swaglabs,
    SwaglabsAuthenticationError,
    SwaglabsItemNotFoundError,
)


# debuging test to be deleted
def test_browser():
    browser1 = browser.browser()
    swag = Swaglabs()
    swag.configure()
    browser2 = swag._browser
    assert browser1 is browser2


@pytest.fixture(scope="module")
def credentials(module_env_vars: dict) -> Union[vault.SecretContainer, dict]:
    """A vault with Swag Labs credentials.

    Vault Secrets will only work if test are ran via rcc. If
    vault secrets are not found, secrets will be loaded from
    environment variables "USERNAME" and "PASSWORD". If those
    are not found, a dictionary with blank strings will
    be returned and live tests will fail.
    """
    try:
        return vault.get_secret(module_env_vars.get("SECRET_NAME", "swaglabs"))
    except (KeyError, vault.RobocorpVaultError):
        pass
    try:
        return {
            "username": module_env_vars["USERNAME"],
            "password": module_env_vars["PASSWORD"],
        }
    except KeyError:
        return {
            "username": "",
            "password": "",
        }


@pytest.fixture(scope="module")
def swag(module_env_vars: dict) -> Generator[Swaglabs, None, None]:
    """An instantiated Swag Labs automation class"""
    swag = Swaglabs()
    swag.configure(
        base_url=module_env_vars.get("BASE_URL", "https://www.saucedemo.com"),
        browser_configuration={"headless": True},
    )
    yield swag
    swag.close()


def test_swaglabs_login_error(swag: Swaglabs) -> None:
    """Tests that an error is raised with no credentials"""
    with pytest.raises(SwaglabsAuthenticationError):
        swag.login()


@pytest.fixture(scope="module")
def swag_logged_in(
    swag: Swaglabs, credentials: vault.SecretContainer
) -> Generator[Swaglabs, None, None]:
    """Tests that a user can login to Swag Labs"""
    swag.login(username=credentials["username"], password=credentials["password"])
    yield swag


@pytest.mark.live
def test_swaglabs_login(
    swag_logged_in: Swaglabs, credentials: vault.SecretContainer
) -> None:
    """Tests that a user can login to Swag Labs"""
    assert swag_logged_in.is_logged_in()


@pytest.mark.live
@pytest.mark.parametrize(
    "item_name, expected_to_be_found",
    [
        ("Sauce Labs Backpack", True),
        ("Sauce Labs Bike Light", True),
        ("Sauce Labs Bolt T-Shirt", True),
        ("Bread Basket Backpack", False),
    ],
)
def test_swaglabs_order(
    swag_logged_in: Swaglabs, item_name: str, expected_to_be_found: bool
) -> None:
    """Tests that a user can order an item"""
    if expected_to_be_found:
        swag_logged_in.order_item(item_name)
    else:
        with pytest.raises(SwaglabsItemNotFoundError):
            swag_logged_in.order_item(item_name)
    assert swag_logged_in.is_item_in_cart(item_name) == expected_to_be_found
