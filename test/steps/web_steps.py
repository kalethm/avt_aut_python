# -*- coding: utf-8 -*-
"""
Web step definitions (Selenium + webdriver-manager).

For Playwright-based steps see playwright_steps.py (opt-in per scenario tag).
"""
import logging

from behave import use_step_matcher, step

use_step_matcher("re")

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config
from test.helpers import drivers

logger = logging.getLogger(__name__)


def _driver(context):
    if not hasattr(context, 'web_driver') or context.web_driver is None:
        context.web_driver = drivers.WebDriverManager.get_driver()
    return context.web_driver


def _wait(context):
    return WebDriverWait(_driver(context), config.WEB['explicitly_wait'])


_LOCATORS = {
    'id': By.ID,
    'xpath': By.XPATH,
    'css': By.CSS_SELECTOR,
    'css selector': By.CSS_SELECTOR,
    'name': By.NAME,
    'class name': By.CLASS_NAME,
    'tag name': By.TAG_NAME,
    'link text': By.LINK_TEXT,
    'partial link text': By.PARTIAL_LINK_TEXT,
}


def _find(context, by: str, value: str):
    locator = _LOCATORS.get(by.lower(), By.CSS_SELECTOR)
    return _wait(context).until(EC.presence_of_element_located((locator, value)))


@step(r"(?:que\s+)?ingreso a la aplicación web y navego a la url '([^']+)'")
@step(r"(?:que\s+)?go to url '([^']+)'")
def step_go_to_url(context, url):
    if not url.startswith('http'):
        url = config.WEB['base_url'].rstrip('/') + '/' + url.lstrip('/')
    logger.info("Navigating to %s", url)
    _driver(context).get(url)


@step(r"(?:que\s+)?el título de la página debe ser '([^']+)'")
@step(r"(?:que\s+)?verify the current title is '([^']+)'")
def step_verify_title(context, title):
    actual = _driver(context).title
    assert actual == title, f"Expected title '{title}', got '{actual}'"


@step(r"(?:que\s+)?la URL actual debe ser '([^']+)'")
@step(r"(?:que\s+)?verify the current url is '([^']+)'")
def step_verify_url(context, url):
    actual = _driver(context).current_url
    assert url in actual, f"Expected url containing '{url}', got '{actual}'"


@step(r"(?:que\s+)?escribo '([^']*)' en el elemento con '([^']+)' igual a '([^']+)'")
@step(r"(?:que\s+)?write '([^']*)' in the element with '([^']+)' equals '([^']+)'")
def step_write_in_element(context, text, by, value):
    element = _find(context, by, value)
    element.clear()
    element.send_keys(text)


@step(r"(?:que\s+)?hago clic en el elemento con '([^']+)' igual a '([^']+)'")
@step(r"(?:que\s+)?click the element with '([^']+)' equals '([^']+)'")
def step_click_element(context, by, value):
    element = _wait(context).until(
        EC.element_to_be_clickable((_LOCATORS.get(by.lower(), By.CSS_SELECTOR), value)))
    element.click()


@step(r"(?:que\s+)?el elemento con '([^']+)' igual a '([^']+)' debe contener el texto '([^']+)'")
@step(r"(?:que\s+)?verify the element with '([^']+)' equals '([^']+)' contains text '([^']+)'")
def step_verify_element_text(context, by, value, text):
    element = _find(context, by, value)
    assert text in element.text, f"Element text '{element.text}' does not contain '{text}'"


@step(r"(?:que\s+)?el elemento con '([^']+)' igual a '([^']+)' debe estar visible")
@step(r"(?:que\s+)?verify the element with '([^']+)' equals '([^']+)' is visible")
def step_verify_element_visible(context, by, value):
    element = _find(context, by, value)
    assert element.is_displayed(), f"Element ({by}={value}) is not visible"


@step(r"(?:que\s+)?el elemento con '([^']+)' igual a '([^']+)' no debe estar presente")
@step(r"(?:que\s+)?verify the element with '([^']+)' equals '([^']+)' is not present")
def step_verify_element_absent(context, by, value):
    driver = _driver(context)
    locator = _LOCATORS.get(by.lower(), By.CSS_SELECTOR)
    elements = driver.find_elements(locator, value)
    assert len(elements) == 0, f"Element ({by}={value}) is present but should not be"
