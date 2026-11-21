# -*- coding: utf-8 -*-
"""
Mobile step definitions (Appium) for POS terminals and Android/iOS devices.

Complements pos_steps.py (raw ADB) for scenarios that need UiAutomator2
locators or remote Appium servers (e.g. UFT Digital Lab).
"""
import logging

from behave import use_step_matcher, step

use_step_matcher("re")

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config
from test.helpers import drivers

logger = logging.getLogger(__name__)

_LOCATORS = {
    'accessibility id': AppiumBy.ACCESSIBILITY_ID,
    'id': AppiumBy.ID,
    'xpath': AppiumBy.XPATH,
    'class name': AppiumBy.CLASS_NAME,
    'android uiautomator': AppiumBy.ANDROID_UIAUTOMATOR,
}


def _locator(by: str):
    return _LOCATORS.get(by.lower(), AppiumBy.XPATH)


def _appium_driver(context, device_name=None):
    """Get or create the Appium driver for the given (or current) device."""
    device_name = device_name or getattr(context, 'current_device', None) \
        or config.DEFAULT_POS_DEVICE
    context.current_device = device_name
    if not hasattr(context, 'appium_drivers'):
        context.appium_drivers = {}
    if device_name not in context.appium_drivers:
        context.appium_drivers[device_name] = drivers.AppiumManager.get_driver(device_name)
    return context.appium_drivers[device_name]


@step(r"(?:que\s+)?preparo el dispositivo '?(?P<device>[A-Za-z0-9_]+)'?")
def step_prepare_device(context, device):
    """Create the Appium session for a POS device (lazy)."""
    logger.info("Preparing device %s", device)
    _appium_driver(context, device)


@step(r"(?:que\s+)?la sesión móvil está lista")
@step(r"(?:que\s+)?la sesión móvil está lista en el dispositivo '([^']+)'")
def step_session_ready(context, device=None):
    """Validate the Appium session is active."""
    driver = _appium_driver(context, device) if device else _appium_driver(context)
    assert driver is not None, "Appium session is not active"
    logger.info("Session ready on %s", context.current_device)


@step(r"(?:que\s+)?abro la aplicación del dispositivo")
@step(r"(?:que\s+)?abro la aplicación en el dispositivo '([^']+)'")
def step_open_app(context, device=None):
    driver = _appium_driver(context, device) if device else _appium_driver(context)
    device_cfg = config.POS_DEVICES.get(context.current_device, {})
    package = device_cfg.get('app_package')
    activity = device_cfg.get('app_activity')
    if package and activity:
        driver.activate_app(f"{package}/{activity}")
        logger.info("App launched: %s/%s", package, activity)
    else:
        logger.info("No app_package/app_activity configured; session already on foreground app")


@step(r"(?:que\s+)?presiono el botón atrás en el dispositivo")
def step_press_back(context):
    _appium_driver(context).press_keycode(4)  # Android KEYCODE_BACK


@step(r"(?:que\s+)?presiono el botón home en el dispositivo")
def step_press_home(context):
    _appium_driver(context).press_keycode(3)  # Android KEYCODE_HOME


@step(r"(?:que\s+)?hago tap en el elemento '(?P<by>[^']+)' con valor '(?P<value>[^']+)'")
@step(r"(?:que\s+)?appium click the element with '(?P<by>[^']+)' equals '(?P<value>[^']+)'")
def step_appium_click(context, by, value):
    driver = _appium_driver(context)
    element = WebDriverWait(driver, config.WEB['explicitly_wait']).until(
        EC.element_to_be_clickable((_locator(by), value))
    )
    element.click()


@step(r"(?:que\s+)?escribo '(?P<text>[^']*)' en el elemento '(?P<by>[^']+)' con valor '(?P<value>[^']+)'")
def step_appium_send_keys(context, text, by, value):
    driver = _appium_driver(context)
    element = WebDriverWait(driver, config.WEB['explicitly_wait']).until(
        EC.presence_of_element_located((_locator(by), value))
    )
    element.send_keys(text)


@step(r"(?:que\s+)?el elemento '(?P<by>[^']+)' con valor '(?P<value>[^']+)' debe estar presente")
def step_appium_verify_present(context, by, value):
    driver = _appium_driver(context)
    elements = driver.find_elements(_locator(by), value)
    assert len(elements) > 0, f"Element ({by}={value}) not present"


@step(r"(?:que\s+)?el elemento '(?P<by>[^']+)' con valor '(?P<value>[^']+)' debe contener el texto '(?P<text>[^']+)'")
def step_appium_verify_text(context, by, value, text):
    driver = _appium_driver(context)
    element = WebDriverWait(driver, config.WEB['explicitly_wait']).until(
        EC.presence_of_element_located((_locator(by), value))
    )
    assert text in element.text, \
        f"Expected '{text}' in element text '{element.text}'"
