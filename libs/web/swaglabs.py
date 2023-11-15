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
import random
import string

from typing import Mapping, Optional, Any
from prodict import Prodict

from playwright.sync_api import (
    Locator,
    TimeoutError,
)

from robocorp import log

from . import WebAutomationBase, WebApplicationError, WebBusinessError

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


class Swaglabs(WebAutomationBase):
    """This class provides for the automation of the Swag Labs web site.
    It provides for a context manager to ensure that the user is logged
    out when the automation is complete.
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: str = DEFAULT_URL,  # Note the new default value
        timeout: Optional[float] = None,
        browser_configuration: Optional[Mapping[str, Any]] = None,
        context_configuration: Optional[Mapping[str, Any]] = None,
    ):
        super().__init__(
            username,
            password,
            base_url,
            timeout,
            browser_configuration,
            context_configuration,
        )

    def configure(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        browser_configuration: Optional[Mapping[str, Any]] = None,
        context_configuration: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().configure(
            username,
            password,
            base_url,
            timeout,
            browser_configuration,
            context_configuration,
        )

    # Prodict requires you define a static schema so IDE autocompletion works
    class Locators(Prodict):
        """The locators used by the automation."""

        username: Locator
        password: Locator
        logon_button: Locator
        menu_button: Locator
        close_menu_button: Locator
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
            close_menu_button=self.page.get_by_role("button", name="Close Menu"),
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

    def is_logged_in(self) -> bool:
        """Determine if the user is logged in. Note that none of the calls
        in this method utilize automatic waiting.

        Returns:
            bool: True if the user is logged in, False otherwise.
        """
        if (
            self.base_url is not None
            and self.base_url in self.page.url
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
            except TimeoutError as e:
                raise auth_error from e
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
        except TimeoutError as e:
            raise SwaglabsWebAppError(
                "Failed to go to the order screen on the Swag Labs web site."
            ) from e
        if self.locators.close_menu_button.is_visible():
            self.locators.close_menu_button.click()

    def add_item_to_cart(self, item_name: str) -> None:
        """Order the specified item.

        Args:
            item_name (str): The name of the item to order.

        Raises:
            SwaglabsNotLoggedInError: Raised if the user is not logged in.
            SwaglabsItemNotFoundError: Raised if the item is not found.
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
        except TimeoutError as e:
            raise SwaglabsItemNotFoundError(
                f"The {item_name} item was not found on the Swag Labs web site."
            ) from e

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
        except TimeoutError as e:
            raise SwaglabsWebAppError(
                "Failed to go to the cart on the Swag Labs web site."
            ) from e

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
            log.info("The cart is already empty.")

    def submit_order(self, first_name: str, last_name: str, zip_code: str) -> str:
        """Submits the current order from the cart. You must provide
        customer information for the order.

        Args:
            first_name (str): The first name of the customer.
            last_name (str): The last name of the customer.
            zip_code (str): The zip code of the customer.

        Returns:
            str: The order number of the submitted order.

        Raises:
            SwaglabsNotLoggedInError: Raised if the user is not logged in.
            SwaglabsCartEmptyError: Raised if the cart is empty.
            SwaglabsOrderError: Raised if the order fails.
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
        except TimeoutError as e:
            raise SwaglabsOrderError(
                "Failed to submit the order on the Swag Labs web site."
            ) from e
        order_number = self.get_order_number()
        if order_number is None:
            raise SwaglabsOrderError(
                "Swag Labs web site did not provide an order number."
            )
        return order_number

    def get_order_number(self) -> Optional[str]:
        """Gets the order number from the confirmation page. Note, this
        method skips actionability and visibility checks and returns
        None if the page is not a confirmation page.
        """
        log.info("Getting the order number.")
        if not self.is_logged_in():
            raise SwaglabsNotLoggedInError(
                "Cannot get the order number on the Swag Labs web site when not logged in."
            )
        if not self.locators.order_confirmation.is_visible():
            return None
        return self.generate_mock_order_number()

    def generate_mock_order_number(self, order_number_length: int = 10) -> str:
        """Generates a mock order number. The sauce labs site does not
        actually generate order numbers, so this is mocked to provide
        an example of generating reports from completed work items.
        """
        first_part = "".join(
            random.choices(
                string.digits,
                k=3 if order_number_length > 3 else order_number_length,
            )
        )
        second_part = "".join(
            random.choices(
                string.digits,
                k=order_number_length - len(first_part),
            )
        )
        return f"ON-{first_part}-{second_part}"
