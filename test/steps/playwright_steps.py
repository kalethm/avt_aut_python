# -*- coding: utf-8 -*-
"""
Playwright step definitions (opt-in alternative to Selenium for web tests).

Tag a scenario/feature with @playwright to run it through Playwright instead
of Selenium. Both engines coexist: each keeps its own browser instance.
"""
import logging

from behave import use_step_matcher, step

use_step_matcher("re")

from playwright.sync_api import sync_playwright

import config

logger = logging.getLogger(__name__)


def _pw(context):
    """Lazily start Playwright and return the page."""
    if not hasattr(context, 'pw_page') or context.pw_page is None:
        context._pw = sync_playwright().start()
        browser_name = {'chrome': 'chromium', 'msedge': 'chromium'}.get(
            config.WEB['browser'].lower(), config.WEB['browser'].lower())
        browser = getattr(context._pw, browser_name).launch(headless=config.WEB['headless'])
        context._pw_browser = browser
        context.pw_page = browser.new_page()
        logger.info("Playwright browser started: %s", browser_name)
    return context.pw_page


@step(r"(?:que\s+)?ingreso a la aplicación web con playwright y navego a la url '([^']+)'")
@step(r"(?:que\s+)?go to url with playwright '([^']+)'")
def step_pw_go_to_url(context, url):
    if not url.startswith('http'):
        url = config.WEB['base_url'].rstrip('/') + '/' + url.lstrip('/')
    page = _pw(context)
    logger.info("Playwright navigating to %s", url)
    page.goto(url)


@step(r"(?:que\s+)?el título de la página con playwright debe ser '([^']+)'")
def step_pw_verify_title(context, title):
    actual = _pw(context).title()
    assert actual == title, f"Expected title '{title}', got '{actual}'"


@step(r"(?:que\s+)?con playwright hago clic en el elemento '([^']+)'")
def step_pw_click(context, selector):
    _pw(context).click(selector)


@step(r"(?:que\s+)?con playwright escribo '([^']*)' en el elemento '([^']+)'")
def step_pw_fill(context, selector, text):
    _pw(context).fill(selector, text)


@step(r"(?:que\s+)?con playwright el elemento '([^']+)' debe contener el texto '([^']+)'")
def step_pw_verify_text(context, selector, text):
    element_text = _pw(context).inner_text(selector)
    assert text in element_text, f"Expected '{text}' in '{element_text}'"
