"""Unit tests for the Swag Labs automation class

Tests which interact with the Swag Labs website are marked as live.

This module supports an environment variable file with the following
variables:
 * BASE_URL: The base URL of the Swag Labs website, for testing a non-demo
    website, you should set this to the site's test URL.
 * SECRET_NAME: The name of the secret in the CR vault which contains the
    website credentials.
"""
import os
import pytest
from typing import Generator, Union

from robocorp import vault

# System under test
from libs.web.swaglabs import (
    Swaglabs,
    SwaglabsAuthenticationError,
    SwaglabsItemNotFoundError,
)


@pytest.fixture(scope="module")
def credentials() -> Union[vault.SecretContainer, dict]:
    """A vault with Swag Labs credentials.

    Vault Secrets will only work if test are ran via rcc. If
    vault secrets are not found, secrets will be loaded from
    environment variables "USERNAME" and "PASSWORD". If those
    are not found, a dictionary with blank strings will
    be returned and live tests will fail.
    """
    try:
        return vault.get_secret(os.environ.get("SECRET_NAME", "swaglabs"))
    except (KeyError, vault.RobocorpVaultError):
        pass
    try:
        return {
            "username": os.environ["AUTOMATION_USERNAME"],
            "password": os.environ["AUTOMATION_PASSWORD"],
        }
    except KeyError:
        return {
            "username": "",
            "password": "",
        }


@pytest.fixture(scope="module")
def swag() -> Generator[Swaglabs, None, None]:
    """An instantiated Swag Labs automation class"""
    swag = Swaglabs()
    swag.configure(
        base_url=os.environ.get("BASE_URL", "https://www.saucedemo.com"),
        browser_configuration={"headless": True},
    )
    yield swag
    swag.close()


def test_swaglabs_login_error(swag: Swaglabs) -> None:
    """Tests that an error is raised with no credentials"""
    with pytest.raises(SwaglabsAuthenticationError):
        swag.login()


@pytest.mark.live
def test_swaglabs_locked_out_user(swag: Swaglabs) -> None:
    """Tests that the locked out user throws an error"""
    with pytest.raises(SwaglabsAuthenticationError):
        swag.login(username="locked_out_user", password="secret_sauce")


@pytest.fixture(scope="module")
def swag_logged_in(
    swag: Swaglabs, credentials: vault.SecretContainer
) -> Generator[Swaglabs, None, None]:
    """Tests that a user can login to Swag Labs"""
    swag.login(username=credentials["username"], password=credentials["password"])
    swag.locators.menu_button.click()
    swag.page.get_by_role("link", name="Reset App State").click()
    swag.page.get_by_role("button", name="Close Menu").click()
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
def test_ordering_an_item(
    swag_logged_in: Swaglabs, item_name: str, expected_to_be_found: bool
) -> None:
    """Tests that a user can order an item"""
    if expected_to_be_found:
        swag_logged_in.add_item_to_cart(item_name)
    else:
        with pytest.raises(SwaglabsItemNotFoundError):
            swag_logged_in.add_item_to_cart(item_name)
    assert (
        swag_logged_in.is_item_in_cart(item_name, return_to_last=True)
        == expected_to_be_found
    )
    if not swag_logged_in.is_cart_empty():
        swag_logged_in.clear_cart()
        assert swag_logged_in.is_cart_empty()


@pytest.mark.live
def test_submit_order(swag_logged_in: Swaglabs) -> None:
    """Tests that a user can submit an order"""
    swag_logged_in.add_item_to_cart("Sauce Labs Backpack")
    order_number = swag_logged_in.submit_order("Test", "User", "12345")
    assert order_number is not None
