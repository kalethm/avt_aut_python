# -*- coding: utf-8 -*-
"""
Driver management for web (Selenium + webdriver-manager), API (requests)
and mobile/POS (Appium) tests.

Mirrors the DriverManager concept from the Java Cucumber project:
- one driver instance per logical device
- lazy creation on first use
- central quit at the end of the run
"""
import logging
import threading
from typing import Optional

import requests
from appium import webdriver as appium_webdriver
from appium.options.android import UiAutomator2Options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

import config
from test.helpers.adb_pos import AdbClient

logger = logging.getLogger(__name__)

# Device drivers keyed by logical device name (POS_PAX_1, POS_INGENICO_1, WEB, API...)
_drivers = {}
_adb_clients = {}
_lock = threading.Lock()


# ----------------------------------------------------------------------
# Web (Selenium + webdriver-manager)
# ----------------------------------------------------------------------
class WebDriverManager:
    """Creates and manages Selenium WebDriver instances with auto driver resolution."""

    _instances = {}

    @classmethod
    def get_driver(cls, browser: Optional[str] = None):
        browser = (browser or config.WEB['browser']).lower()
        if browser in cls._instances:
            return cls._instances[browser]

        headless = config.WEB['headless']
        if browser == 'chrome':
            options = ChromeOptions()
            service = ChromeService(ChromeDriverManager().install())
            if headless:
                options.add_argument('--headless=new')
        elif browser == 'firefox':
            options = FirefoxOptions()
            service = FirefoxService(GeckoDriverManager().install())
            if headless:
                options.add_argument('-headless')
        elif browser == 'edge':
            options = EdgeOptions()
            service = EdgeService(EdgeChromiumDriverManager().install())
            if headless:
                options.add_argument('--headless=new')
        else:
            raise ValueError(f"Unsupported browser: {browser}")

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')

        driver = webdriver.Chrome(service=service, options=options) \
            if browser == 'chrome' else \
            webdriver.Firefox(service=service, options=options) \
            if browser == 'firefox' else \
            webdriver.Edge(service=service, options=options)

        driver.implicitly_wait(config.WEB['implicitly_wait'])
        cls._instances[browser] = driver
        logger.info("Web driver created: %s", browser)
        return driver

    @classmethod
    def quit_all(cls):
        for browser, driver in cls._instances.items():
            try:
                driver.quit()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Error closing %s driver: %s", browser, exc)
        cls._instances.clear()


# ----------------------------------------------------------------------
# API (requests.Session)
# ----------------------------------------------------------------------
class ApiClient:
    """Shared requests.Session for API tests."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        self.last_response = None

    def request(self, method: str, url: str, **kwargs):
        kwargs.setdefault('timeout', config.API['timeout'])
        self.last_response = self.session.request(method.upper(), url, **kwargs)
        return self.last_response


# ----------------------------------------------------------------------
# Mobile / POS (Appium)
# ----------------------------------------------------------------------
class AppiumManager:
    """
    Creates Appium sessions per logical device.

    Supports a local Appium server or a remote one such as UFT Digital Lab
    (set APPIUM_SERVER_URL env var or .env).
    """

    @staticmethod
    def capabilities_for(device_name: str) -> dict:
        device = config.POS_DEVICES.get(device_name)
        if not device:
            raise ValueError(f"Device '{device_name}' not declared in config.POS_DEVICES")

        caps = {
            'platformName': config.APPIUM['platform_name'],
            'appium:automationName': config.APPIUM['automation_name'],
            'appium:udid': device['udid'],
            'appium:noReset': config.APPIUM['no_reset'],
            'appium:fullReset': config.APPIUM['full_reset'],
            'appium:newCommandTimeout': config.APPIUM['new_command_timeout'],
        }
        if device.get('app_package'):
            caps['appium:appPackage'] = device['app_package']
        if device.get('app_activity'):
            caps['appium:appActivity'] = device['app_activity']
        return caps

    @classmethod
    def get_driver(cls, device_name: str):
        with _lock:
            if device_name in _drivers:
                return _drivers[device_name]

            caps = cls.capabilities_for(device_name)
            options = UiAutomator2Options().load_capabilities(caps)
            driver = appium_webdriver.Remote(config.APPIUM['server_url'], options=options)
            _drivers[device_name] = driver
            logger.info("Appium session created for %s", device_name)
            return driver


# ----------------------------------------------------------------------
# ADB clients per POS device
# ----------------------------------------------------------------------
def get_adb_client(device_name: str) -> AdbClient:
    """Return (creating if needed) the AdbClient bound to a POS device serial."""
    with _lock:
        if device_name not in _adb_clients:
            device = config.POS_DEVICES.get(device_name)
            if not device:
                raise ValueError(f"Device '{device_name}' not declared in config.POS_DEVICES")
            _adb_clients[device_name] = AdbClient(serial=device.get('adb_serial', ''))
        return _adb_clients[device_name]


# ----------------------------------------------------------------------
# Lifecycle
# ----------------------------------------------------------------------
def quit_all():
    """Close every driver/session created during the run."""
    for name, driver in list(_drivers.items()):
        try:
            driver.quit()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Error closing appium driver %s: %s", name, exc)
    _drivers.clear()
    WebDriverManager.quit_all()
    _adb_clients.clear()
