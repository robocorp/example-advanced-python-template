"""This module is an example of a webpage automation class. It provides
for a class that can be used to automate the Swag Labs website. The
automation class provides for ways to login, manipulate the site, 
and place orders. It will raise custom errors depending on what happens
during the automation process.

It also provides a context manager to ensure that the user is logged
out when the automation is complete.
"""
from typing import Mapping, Optional, Any
from playwright.sync_api import (
    Browser as PlaywrightBrowser,
    BrowserContext,
    Page,
    Locator,
    TimeoutError,
)

from robocorp import browser, log

from web import WebAutomationError

DEFAULT_URL = "https://www.saucedemo.com/"


class SwaglabsWebError(WebAutomationError):
    """Base class for all Swag Labs web automation errors."""


class SwaglabsNotLoggedInError(SwaglabsWebError):
    """Raised when the Swag Labs web site is not logged in."""


class SwaglabsAuthenticationError(SwaglabsWebError):
    """Raised when the Swag Labs web site authentication fails."""


class SwaglabsItemNotFoundError(SwaglabsWebError):
    """Raised when the Swag Labs web site item is not found."""


class Swaglabs:
    """This class provides for the automation of the Swag Labs web site.
    It provides for a context manager to ensure that the user is logged
    out when the automation is complete.
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: str = DEFAULT_URL,
        browser_configuration: Optional[Mapping[str, Any]] = None,
        context_configuration: Optional[Mapping[str, Any]] = None,
    ):
        """Initialize the Swag Labs automation class.

        Note: for the available browser and context configuration options
        see the documentation for the robocorp.browser module and the
        Playwright package.

        Args:
            url (str): The URL of the Swag Labs web site. If not provided
                it will default to the live site (https://www.saucedemo.com/)
            username (str): The username to use to login.
            password (str): The password to use to login.
            browser_configuration (Mapping): The browser configuration to use.
            context_configuration (Mapping): The context configuration to use.
        """
        self.base_url = DEFAULT_URL
        self.username = None
        self.password = None
        self._browser_config = {}
        if base_url is not None:
            self.base_url = base_url
        self.configure(
            username, password, base_url, browser_configuration, context_configuration
        )

    def __enter__(self) -> "Swaglabs":
        """Enter the context manager. This will create a browser instance
        and navigate to the Swag Labs web site.
        """
        self.configure()
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Exit the context manager. This will close the browser instance."""
        self.close()

    @property
    def browser(self) -> PlaywrightBrowser:
        """The browser instance. Calling this before configuring
        the automation will cause the automation to be configured
        with the default configuration.
        """
        if self._browser is None:
            self.configure()
        return self._browser

    @property
    def context(self) -> BrowserContext:
        """The browser context. Calling this before configuring
        the automation will cause the automation to be configured
        with the default configuration.
        """
        if self._context is None:
            self.configure()
        return self._context

    @property
    def page(self) -> Page:
        """The browser page. Calling this before configuring
        the automation will cause the automation to be configured
        with the default configuration.
        """
        if self._page is None:
            self.configure()
        return self._page

    # TODO: Re architect this so intellisense returns locators as you are
    # building the class methods.
    def _locators(self, locator_name: str) -> Locator:
        """Returns a mapping of common locators used by the automation."""
        if self._page is None:
            raise SwaglabsWebError(
                "Cannot get locators before configuring the automation."
            )
        return {
            "username": self.page.get_by_placeholder("Username"),
            "password": self.page.get_by_placeholder("Password"),
            "login_button": self.page.get_by_role("button", name="Login"),
            "menu_button": self.page.get_by_role("button", name="Open Menu"),
            "logout_button": self.page.get_by_role("link", name="Logout"),
            "all_items_link": self.page.get_by_role("link", name="All Items"),
            "cart_button": self._page.locator("//div[@id='shopping_cart_container']"),
            "inventory_container": self._page.locator(
                "//div[@id='inventory_container']"
            ),
        }[locator_name]

    def configure(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: Optional[str] = None,
        browser_configuration: Optional[Mapping[str, Any]] = None,
        context_configuration: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Configure the Swag Labs automation class. If robocorp.browser
        was already configured before using this method, the new
        browser and context configuration will be ignored.

        Args:
            browser_configuration (mapping): The keyword arguments to use to configure the browser.
            context_configuration (mapping): The keyword arguments to use to configure the context.
        """
        if isinstance(username, str):
            self.username = username
        elif username is not None:
            raise TypeError(f"username must be a string, not {type(username).__name__}")
        if isinstance(password, str):
            self.password = password
        elif password is not None:
            raise TypeError(f"password must be a string, not {type(password).__name__}")
        if isinstance(base_url, str):
            self.base_url = base_url
        elif base_url is not None:
            raise TypeError(f"url must be a string, not {type(base_url).__name__}")
        if browser_configuration is not None:
            browser.configure(**browser_configuration)
        if context_configuration is not None:
            browser.configure_context(**context_configuration)
        self._browser = browser.browser()
        self._context = browser.context()
        self._page = browser.page()

    def _is_logged_in(self) -> bool:
        """Determine if the user is logged in. Note that none of the calls
        in this method utilize automatic waiting.

        Returns:
            bool: True if the user is logged in, False otherwise.
        """
        if (
            self._page is not None
            and self.base_url in self._page.url
            and self._locators("cart_button").is_visible()
        ):
            return True
        return False

    def login(self, username: Optional[str] = None, password: Optional[str] = None):
        """Login to the Swag Labs web site. If the username and password
        are not provided, the username and password provided when the
        automation was created will be used. If called before configuring
        the automation, the default configuration will be used.

        Args:
            username (str): The username to use to login.
            password (str): The password to use to login.

        Raises:
            SwaglabsAuthenticationError: Raised if the authentication fails.
        """
        log.info("Logging in to the Swag Labs web site.")
        if not self._is_logged_in():
            self.configure(username, password)
            if self.username is None or self.password is None:
                raise SwaglabsAuthenticationError(
                    "Username and password must be provided to login to the Swag Labs web site."
                )
            self._locators("username").fill(self.username)
            self._locators("password").fill(self.password)
            self._locators("logon_button").click()
            self._locators("cart_button").wait_for()
            if not self._is_logged_in():
                raise SwaglabsAuthenticationError(
                    "Failed to login to the Swag Labs web site."
                )

    def logout(self):
        """Logout of the Swag Labs web site.

        Raises:
            SwaglabsNotLoggedInError: Raised if the user is not logged in.
        """
        log.info("Logging out of the Swag Labs web site.")
        if not self._is_logged_in():
            raise SwaglabsNotLoggedInError(
                "Cannot logout of the Swag Labs web site when not logged in."
            )
        self._locators("menu_button").click()
        self._locators("logout_button").click()

    def close(self):
        """Logs out and then closes the browser."""
        log.info("Closing the Swag Labs web site.")
        if self._is_logged_in():
            self.logout()
        # Note: browser and context are not closed based on the
        # assumption that the browser is shared with other automation
        # classes, see the robocorp.browser module for additional
        # information.
        if self._page is not None:
            self._page.close()

    def go_to_order_screen(self) -> None:
        """Go to the order screen.

        Raises:
            SwaglabsNotLoggedInError: Raised if the user is not logged in.
        """
        log.info("Going to the order screen.")
        if not self._is_logged_in():
            raise SwaglabsNotLoggedInError(
                "Cannot go to the order screen on the Swag Labs web site when not logged in."
            )
        self._locators("cart_button").click()

    def order_item(self, item_name: str) -> None:
        """Order the specified item.

        Args:
            item_name (str): The name of the item to order.

        Raises:
            SwaglabsNotLoggedInError: Raised if the user is not logged in.
        """
        log.info(f"Ordering the {item_name} item.")
        if not self._is_logged_in():
            raise SwaglabsNotLoggedInError(
                "Cannot order items from the Swag Labs web site when not logged in."
            )
        if not self._locators("inventory_container").is_visible():
            self.go_to_order_screen()
        try:
            self._locators("inventory_container").get_by_role(
                "link", name=item_name
            ).click()
        except TimeoutError:
            raise SwaglabsItemNotFoundError(
                f"The {item_name} item was not found on the Swag Labs web site."
            )
