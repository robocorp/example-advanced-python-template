"""This module is an example of a webpage automation class. It provides
for a class that can be used to automate the Swag Labs website. The
automation class provides for ways to login, manipulate the site, 
and place orders. It will raise custom errors depending on what happens
during the automation process. These errors all derive from the 
robocorp.workitems.ApplicationException or robocorp.workitems.BusinessException
classes, thus when raised inside of a work item Input context manager,
they will be handled as expected.

It also provides a context manager to ensure that the user is logged
out when the automation is complete.
"""
from typing import Mapping, Optional, Any
from prodict import Prodict

from playwright.sync_api import (
    Browser as PlaywrightBrowser,
    BrowserContext,
    Page,
    Locator,
    TimeoutError,
)

from robocorp import browser, log

from web import WebApplicationError, WebBusinessError

DEFAULT_URL = "https://www.saucedemo.com/"


### APPLICATION ERRORS ###
class SwaglabsWebAppError(WebApplicationError):
    """Base class for all Swag Labs web application errors."""


class SwaglabsNotLoggedInError(SwaglabsWebAppError):
    """Raised when the Swag Labs web site is not logged in."""


class SwaglabsAuthenticationError(SwaglabsWebAppError):
    """Raised when the Swag Labs web site authentication fails."""


class SwaglabsCartEmptyError(SwaglabsWebAppError):
    """Raised when the Swag Labs web site cart is empty during an
    attempt to submit an order."""


class SwaglabsOrderError(SwaglabsWebAppError):
    """Raised when the Swag Labs web site order fails."""


### BUSINESS ERRORS ###
class SwaglabsWebBusinessError(WebBusinessError):
    """Base class for all Swag Labs web business errors."""


class SwaglabsItemNotFoundError(SwaglabsWebBusinessError):
    """Raised when the Swag Labs web site item is not found."""


class Swaglabs:
    """This class provides for the automation of the Swag Labs web site.
    It provides for a context manager to ensure that the user is logged
    out when the automation is complete.
    """

    # TODO: Make an ABC that this can derive from.

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: str = DEFAULT_URL,
        timeout: float = 10000.0,
        browser_configuration: Optional[Mapping[str, Any]] = None,
        context_configuration: Optional[Mapping[str, Any]] = None,
    ):
        """Initialize the Swag Labs automation class.

        Note: for the available browser and context configuration options
        see the documentation for the robocorp.browser module and the
        Playwright package.

        Args:
            username (str): The username to use to login.
            password (str): The password to use to login.
            base_url (str): The URL of the Swag Labs web site. If not provided
                it will default to the live site (https://www.saucedemo.com/)
            timeout (int): The timeout to use for the automation.
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
            username,
            password,
            base_url,
            timeout,
            browser_configuration,
            context_configuration,
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

    # Prodict requires you define a static schema so IDE autocompletion works
    class Locators(Prodict):
        """The locators used by the automation."""

        username: Locator
        password: Locator
        logon_button: Locator
        menu_button: Locator
        logout_button: Locator
        all_items_link: Locator
        cart_button: Locator
        cart_page: Locator
        cart_items: Locator
        cart_items_container: Locator
        cart_badge: Locator
        inventory_container: Locator
        inventory_items: Locator
        checkout_button: Locator
        customer_first_name: Locator
        customer_last_name: Locator
        customer_zip_code: Locator
        customer_continue_button: Locator
        order_finish_button: Locator
        order_confirmation: Locator

    @property
    def locators(self) -> Locators:
        """The locators used by the automation."""

        return self.Locators(
            username=self.page.get_by_placeholder("Username"),
            password=self.page.get_by_placeholder("Password"),
            logon_button=self.page.get_by_role("button", name="Login"),
            menu_button=self.page.get_by_role("button", name="Open Menu"),
            logout_button=self.page.get_by_role("link", name="Logout"),
            all_items_link=self.page.get_by_role("link", name="All Items"),
            cart_button=self.page.locator("#shopping_cart_container"),
            cart_page=self.page.get_by_text("Your Cart", exact=True),
            cart_items=self.page.locator("div.cart_item"),
            cart_items_container=self.page.locator("#cart_contents_container"),
            cart_badge=self.page.locator("#shopping_cart_container").locator(
                "span.shopping_cart_badge"
            ),
            inventory_container=self.page.locator(
                "div#inventory_container.inventory_container"
            ),
            inventory_items=self.page.locator("div.inventory_item"),
            checkout_button=self.page.get_by_role("button", name="Checkout"),
            customer_first_name=self.page.get_by_placeholder("First Name"),
            customer_last_name=self.page.get_by_placeholder("Last Name"),
            customer_zip_code=self.page.get_by_placeholder("Zip/Postal Code"),
            customer_continue_button=self.page.get_by_role("button", name="Continue"),
            order_finish_button=self.page.get_by_role("button", name="Finish"),
            order_confirmation=self.page.get_by_text(
                "Your order has been dispatched, and will arrive just as fast as the pony can get there!"
            ),
        )

    def configure(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 10000.0,
        browser_configuration: Optional[Mapping[str, Any]] = None,
        context_configuration: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Configure the Swag Labs automation class. If robocorp.browser
        was already configured before using this method, the new
        browser and context configuration will be ignored.

        Note: this does not open the page to the base url. To do that
        use the open or login methods.

        Args:
            username (str): The username to use to login.
            password (str): The password to use to login.
            base_url (str): The base URL of the Swag Labs web site.
            timeout (float): The timeout to use when waiting for elements.
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
        self._context.set_default_timeout(timeout)
        self._page = browser.page()

    def open(self) -> None:
        """Open the Swag Labs web site."""
        self.page.goto(self.base_url)

    def is_logged_in(self) -> bool:
        """Determine if the user is logged in. Note that none of the calls
        in this method utilize automatic waiting.

        Returns:
            bool: True if the user is logged in, False otherwise.
        """
        if (
            self._page is not None
            and self.base_url in self._page.url
            and self.locators.cart_button.is_visible()
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
        if not self.is_logged_in():
            self.configure(username, password)
            if self.username is None or self.password is None:
                raise SwaglabsAuthenticationError(
                    "Username and password must be provided to login to the Swag Labs web site."
                )
            self.open()
            self.locators.username.fill(self.username)
            self.locators.password.fill(self.password)
            self.locators.logon_button.click()
            auth_error = SwaglabsAuthenticationError(
                "Failed to login to the Swag Labs web site."
            )
            try:
                self.locators.cart_button.wait_for()
            except TimeoutError:
                raise auth_error
            if not self.is_logged_in():
                raise auth_error

    def logout(self):
        """Logout of the Swag Labs web site.

        Raises:
            SwaglabsNotLoggedInError: Raised if the user is not logged in.
        """
        log.info("Logging out of the Swag Labs web site.")
        if not self.is_logged_in():
            raise SwaglabsNotLoggedInError(
                "Cannot logout of the Swag Labs web site when not logged in."
            )
        self.locators.menu_button.click()
        self.locators.logout_button.click()

    def close(self):
        """Logs out and then closes the browser."""
        log.info("Closing the Swag Labs web site.")
        if self.is_logged_in():
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
            SwaglabsWebError: Raised if the order screen cannot be reached.
        """
        log.info("Going to the order screen.")
        if not self.is_logged_in():
            raise SwaglabsNotLoggedInError(
                "Cannot go to the order screen on the Swag Labs web site when not logged in."
            )
        self.locators.menu_button.click()
        self.locators.all_items_link.click()
        try:
            self.locators.inventory_container.wait_for()
        except TimeoutError:
            raise SwaglabsWebAppError(
                "Failed to go to the order screen on the Swag Labs web site."
            )

    def add_item_to_cart(self, item_name: str) -> None:
        """Order the specified item.

        Args:
            item_name (str): The name of the item to order.

        Raises:
            SwaglabsNotLoggedInError: Raised if the user is not logged in.
        """
        log.info(f"Ordering the {item_name} item.")
        if not self.is_logged_in():
            raise SwaglabsNotLoggedInError(
                "Cannot order items from the Swag Labs web site when not logged in."
            )
        if not self.locators.inventory_container.is_visible():
            self.go_to_order_screen()
        try:
            self.locators.inventory_items.filter(has_text=item_name).get_by_role(
                "button", name="Add to cart"
            ).click()
        except TimeoutError:
            raise SwaglabsItemNotFoundError(
                f"The {item_name} item was not found on the Swag Labs web site."
            )

    def go_to_cart(self) -> None:
        """Go to the cart.

        Raises:
            SwaglabsNotLoggedInError: Raised if the user is not logged in.
            TimeoutError: Raised if the cart button is not visible.
        """
        log.info("Going to the cart.")
        if not self.is_logged_in():
            raise SwaglabsNotLoggedInError(
                "Cannot go to the cart on the Swag Labs web site when not logged in."
            )
        if self.locators.cart_page.is_visible():
            return
        self.locators.cart_button.click()
        try:
            self.locators.cart_page.wait_for()
        except TimeoutError:
            raise SwaglabsWebAppError(
                "Failed to go to the cart on the Swag Labs web site."
            )

    def is_item_in_cart(self, item_name: str, *, return_to_last: bool = False) -> bool:
        """Determine if the specified item is in the cart.

        Args:
            item_name (str): The name of the item to check.
            return_to_last (bool): If True, the automation will return to the
                last page it was on before checking the cart.

        Returns:
            bool: True if the item is in the cart, False otherwise.

        Raises:
            SwaglabsNotLoggedInError: Raised if the user is not logged in.
            SwaglabsItemNotFoundError: Raised if the item is not found in
                the cart.
            TimeoutError: Raised if the cart button is not visible.
        """
        log.info(f"Determining if the {item_name} item is in the cart.")
        if not self.is_logged_in():
            raise SwaglabsNotLoggedInError(
                "Cannot determine if items are in the cart on the Swag Labs web site when not logged in."
            )
        self.go_to_cart()
        return_value = False
        if self.locators.cart_items_container.get_by_role(
            "link", name=item_name
        ).is_visible():
            return_value = True
        if return_to_last:
            self.page.go_back()
        return return_value

    def is_cart_empty(self) -> bool:
        """Checks if the cart is empty by looking at the badge count
        superimpsoed on the cart button. Note, this method skips
        actionability and visibility checks.
        """
        log.info("Checking if the cart is empty.")
        if not self.is_logged_in():
            raise SwaglabsNotLoggedInError(
                "Cannot determine if the cart is empty on the Swag Labs web site when not logged in."
            )
        return not self.locators.cart_badge.is_visible()

    def clear_cart(self) -> None:
        """Empties the cart, essentially cancelling the order."""
        log.info("Clearing the cart.")
        if not self.is_logged_in():
            raise SwaglabsNotLoggedInError(
                "Cannot clear the cart on the Swag Labs web site when not logged in."
            )
        if not self.is_cart_empty():
            self.go_to_cart()
            for item in self.locators.cart_items.all():
                item_remove_button = item.get_by_role("button", name="Remove")
                item_remove_button.click()
                item_remove_button.wait_for(state="hidden", timeout=10000.0)
        else:
            log.warn("The cart is already empty.")

    def submit_order(self, first_name: str, last_name: str, zip_code: str) -> None:
        """Submits the current order from the cart. You must provide
        customer information for the order.

        Args:
            first_name (str): The first name of the customer.
            last_name (str): The last name of the customer.
            zip_code (str): The zip code of the customer.

        Raises:
            SwaglabsNotLoggedInError: Raised if the user is not logged in.
            SwaglabsCartEmptyError: Raised if the cart is empty.
        """
        log.info("Submitting the order.")
        if not self.is_logged_in():
            raise SwaglabsNotLoggedInError(
                "Cannot submit the order on the Swag Labs web site when not logged in."
            )
        if self.is_cart_empty():
            raise SwaglabsCartEmptyError(
                "Cannot submit the order on the Swag Labs web site when the cart is empty."
            )
        self.go_to_cart()
        self.locators.checkout_button.click()
        self.locators.customer_first_name.fill(first_name)
        self.locators.customer_last_name.fill(last_name)
        self.locators.customer_zip_code.fill(zip_code)
        self.locators.customer_continue_button.click()
        self.locators.order_finish_button.click()
        try:
            self.locators.order_confirmation.wait_for()
        except TimeoutError:
            raise SwaglabsOrderError(
                "Failed to submit the order on the Swag Labs web site."
            )
