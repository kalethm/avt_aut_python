# -*- coding: utf-8 -*-
"""
Page Object Model (POM) base class for Selenium web tests.

Pages encapsulate the locators and actions of a single view so step
definitions stay free of selector logic. The generic locator steps in
web_steps.py keep working; use pages for flows worth reusing.
"""
import logging

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config
from test.helpers import drivers

logger = logging.getLogger(__name__)


class BasePage:
    """Base class for Selenium page objects.

    Subclasses define ``url`` and locator tuples, e.g.::

        class LoginPage(BasePage):
            url = '/login'
            USER_INPUT = (By.ID, 'user')
    """

    url = ''  # path relative to config.WEB['base_url'], or absolute

    def __init__(self, driver=None):
        self.driver = driver or drivers.WebDriverManager.get_driver()
        self.wait = WebDriverWait(self.driver, config.WEB['explicitly_wait'])

    def open(self):
        """Navigate to the page url and return self for chaining."""
        url = self.url if self.url.startswith('http') else \
            config.WEB['base_url'].rstrip('/') + '/' + self.url.lstrip('/')
        logger.info("Opening page %s", url)
        self.driver.get(url)
        return self

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text, clear=True):
        element = self.find(locator)
        if clear:
            element.clear()
        element.send_keys(text)

    def text_of(self, locator):
        return self.find(locator).text

    def is_visible(self, locator):
        return self.find(locator).is_displayed()

    def scroll_into_view(self, locator):
        element = self.find(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element)
        return element

    def js_click(self, locator):
        element = self.find(locator)
        self.driver.execute_script("arguments[0].click();", element)

    def safe_click(self, locator):
        """Normal click, falling back to a JS click when ads/overlays intercept it."""
        try:
            self.click(locator)
        except Exception:  # noqa: BLE001
            self.js_click(locator)
