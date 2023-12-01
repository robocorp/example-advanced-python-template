"""The web package is an example of a sub-package focusing on automating
various web sites. In this repository, there is only one, but in a 
more complex example, you would have potentially many more.

Note: In many Python use cases, all errors are collected in one module,
but in this repo, only general errors are included in the errors modules
and specific errors are defined within each automation module.
"""
from abc import ABC, abstractmethod
from typing import Optional, Mapping, Any
from typing_extensions import Self
from prodict import Prodict

from playwright.sync_api import (
    Browser as PlaywrightBrowser,
    BrowserContext,
    Page,
)

from robocorp import browser, log

from ..errors import ApplicationError, BusinessError


class WebApplicationError(ApplicationError):
    """Base class for all web automation errors."""


class WebBusinessError(BusinessError):
    """Base class for all web automation business errors."""


class WebAutomationBase(ABC):
    """A base class for web automations. It includes several methods
    and properties which are already implemented but may be overridden,
    in addition, it includes several methods which must be implemented.
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        browser_configuration: Optional[Mapping[str, Any]] = None,
        context_configuration: Optional[Mapping[str, Any]] = None,
    ):
        """Initializes the web automation.

        Note: for the available browser and context configuration options
        see the documentation for the robocorp.browser module and the
        Playwright package.

        Args:
            username: The username to use for authentication.
            password: The password to use for authentication.
            base_url: The base URL to use for the web automation.
            timeout: The timeout to use for the web automation.
            browser_configuration: The browser configuration to use for the
                web automation.
            context_configuration: The context configuration to use for the
                web automation.
        """
        self._configured = False
        self.username = None
        self.password = None
        self.base_url = None
        if (
            username is not None
            or password is not None
            or base_url is not None
            or timeout is not None
            or (browser_configuration is not None and len(browser_configuration) > 0)
            or (context_configuration is not None and len(context_configuration) > 0)
        ):
            self.configure(
                username,
                password,
                base_url,
                timeout,
                browser_configuration,
                context_configuration,
            )

    @abstractmethod
    def configure(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        browser_configuration: Optional[Mapping[str, Any]] = None,
        context_configuration: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Configures the web automation. If robocorp.browser
        was already configured before using this method, the new
        browser and context configuration will be ignored.

        Note: this does not open the page to the base url. To do that
        use the open or login methods.

        For classes which inherit from this class, you must override
        this method, but can choose to use it as a super method if
        you do not need to override the default implementation.

        Args:
            username (str): The username to use for authentication.
            password (str): The password to use for authentication.
            base_url (str): The base URL to use for the web automation.
            timeout (float): The timeout to use for the web automation.
            browser_configuration (mapping): The browser configuration to use for the
                web automation.
            context_configuration (mapping): The context configuration to use for the
                web automation.
        """
        if timeout is None:
            timeout = 10000.0
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
        browser.context().set_default_timeout(timeout)
        self._configured = True

    @property
    def browser(self) -> PlaywrightBrowser:
        """The browser instance. Calling this before configuring
        the automation will cause the automation to be configured
        with the default configuration.
        """
        if self._configured == False:
            self.configure()
        return browser.browser()

    @property
    def context(self) -> BrowserContext:
        """The browser context. Calling this before configuring
        the automation will cause the automation to be configured
        with the default configuration.
        """
        if self._configured == False:
            self.configure()
        return browser.context()

    @property
    def page(self) -> Page:
        """The browser page. Calling this before configuring
        the automation will cause the automation to be configured
        with the default configuration.
        """
        if self._configured == False:
            self.configure()
        return browser.page()

    class Locators(Prodict):
        """A class which defines the locators for the web automation.

        You must define a subclass within your automation module which
        implements the Prodict static schema to allow for IDE completion.
        For example:

        class Locators(Prodict):
            login_button: Locator
            username_field: Locator
            password_field: Locator
        """

    @property
    @abstractmethod
    def locators(self) -> Locators:
        """A dictionary of locators to use for the web automation. This
        property must be implemented by subclasses. For example:

        @property
        def locators(self) -> Locators:
            return self.Locators(
                login_button=self.page.get_by_test_id("login-button"),
                username_field=self.page.get_by_test_id("user-name"),
                password_field=self.page.get_by_test_id("password"),
            )

        """
        raise NotImplementedError()

    def open(self) -> None:
        """Opens the web site to the base URL.

        The default method will open the page to the base URL, but
        subclasses can override this method to do additional work
        before opening the page. Note, however, this method should
        not perform the login work.
        """
        if self.base_url is None:
            raise WebApplicationError("Base URL not configured.")
        self.page.goto(self.base_url)

    @abstractmethod
    def is_logged_in(self) -> bool:
        """Checks if the user is logged in.

        This method must be implemented by subclasses.
        """
        raise NotImplementedError()

    @abstractmethod
    def login(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        """Logs into the web site.

        This method must be implemented by subclasses.
        """
        raise NotImplementedError()

    @abstractmethod
    def logout(self) -> None:
        """Logs out of the web site.

        This method must be implemented by subclasses.
        """
        raise NotImplementedError()

    def close(self) -> None:
        """Logs out and then closes the browser page.

        Note: the browser and the context are not closed as required
        by the robocorp-browser framework, see that package for
        additional information.
        """
        log.info("Closing browser.")
        if self.is_logged_in():
            self.logout()
        if self._configured == True:
            self.page.close()

    def __enter__(self) -> Self:
        """Enter the context manager. This will create a browser instance
        and login to the web site.
        """
        self.configure()
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit the context manager. This will close the page managed
        by the browser library."""
        self.close()
