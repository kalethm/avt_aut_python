# -*- coding: utf-8 -*-
"""Example page object for example.com (see features/web/example_web.feature)."""
from selenium.webdriver.common.by import By

from test.pages.base_page import BasePage


class ExampleDomainPage(BasePage):
    url = 'https://example.com'

    PARAGRAPH = (By.XPATH, '//p[@lang="en"]')
    MORE_INFO_LINK = (By.TAG_NAME, 'a')

    def paragraph_text(self):
        return self.text_of(self.PARAGRAPH)

    def more_info_link_is_visible(self):
        return self.is_visible(self.MORE_INFO_LINK)
