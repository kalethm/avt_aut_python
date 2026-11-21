# -*- coding: utf-8 -*-
"""Page object for the DemoQA Student Registration Form (Practice Form)."""
from selenium.webdriver.common.by import By

from test.pages.base_page import BasePage


class PracticeFormPage(BasePage):
    url = 'https://demoqa.com/automation-practice-form'

    FORM = (By.ID, 'userForm')
    FIRST_NAME = (By.ID, 'firstName')
    LAST_NAME = (By.ID, 'lastName')
    EMAIL = (By.ID, 'userEmail')
    MOBILE = (By.ID, 'userNumber')
    DOB_INPUT = (By.ID, 'dateOfBirthInput')
    SUBJECTS_INPUT = (By.ID, 'subjectsInput')
    ADDRESS = (By.ID, 'currentAddress')
    PICTURE = (By.ID, 'uploadPicture')
    STATE = (By.CSS_SELECTOR, '#state')
    CITY = (By.CSS_SELECTOR, '#city')
    SUBMIT = (By.ID, 'submit')
    SUCCESS_MODAL = (By.ID, 'example-modal-sizes-title-lg')

    GENDERS = {
        'Male': 'gender-radio-1',
        'Female': 'gender-radio-2',
        'Other': 'gender-radio-3',
    }
    HOBBIES = {
        'Sports': 'hobbies-checkbox-1',
        'Reading': 'hobbies-checkbox-2',
        'Music': 'hobbies-checkbox-3',
    }
    FIELDS = {
        'First Name': FIRST_NAME,
        'Last Name': LAST_NAME,
        'Email': EMAIL,
        'Mobile': MOBILE,
        'Date of Birth': DOB_INPUT,
        'Current Address': ADDRESS,
    }

    def fill_form(self, data):
        """Fill the whole form from a dict (see settings/data/practice_form.json)."""
        self.type(self.FIRST_NAME, data['first_name'])
        self.type(self.LAST_NAME, data['last_name'])
        if data.get('email'):
            self.type(self.EMAIL, data['email'])
        self.select_gender(data['gender'])
        if data.get('mobile'):
            self.type(self.MOBILE, data['mobile'])
        if data.get('date_of_birth'):
            self.set_date_of_birth(data['date_of_birth'])
        for subject in data.get('subjects', []):
            self.add_subject(subject)
        self.check_hobbies(data.get('hobbies', []))
        if data.get('picture'):
            self.upload_picture(data['picture'])
        if data.get('current_address'):
            self.type(self.ADDRESS, data['current_address'])
        if data.get('state'):
            self.select_state(data['state'])
        if data.get('city'):
            self.select_city(data['city'])
        return self

    def select_gender(self, gender):
        self.safe_click((By.CSS_SELECTOR, f"label[for='{self.GENDERS[gender]}']"))

    def check_hobbies(self, hobbies):
        for hobby in hobbies:
            self.safe_click(
                (By.CSS_SELECTOR, f"label[for='{self.HOBBIES[hobby]}']"))

    def add_subject(self, subject):
        element = self.find(self.SUBJECTS_INPUT)
        element.send_keys(subject)
        element.send_keys('\ue007')  # ENTER

    def set_date_of_birth(self, value):
        element = self.find(self.DOB_INPUT)
        self.driver.execute_script(
            "const setter = Object.getOwnPropertyDescriptor("
            "window.HTMLInputElement.prototype, 'value').set;"
            "setter.call(arguments[0], arguments[1]);"
            "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
            element, value)

    def upload_picture(self, file_path):
        self.find(self.PICTURE).send_keys(file_path)

    def _select_react_dropdown(self, container, option_text):
        """Type-and-enter selection for the react-select state/city dropdowns."""
        self.scroll_into_view(container)
        input_el = self.find((By.CSS_SELECTOR, f'{container[1]} input'))
        input_el.send_keys(option_text)
        input_el.send_keys('\ue007')  # ENTER

    def select_state(self, state):
        self._select_react_dropdown(self.STATE, state)

    def select_city(self, city):
        self._select_react_dropdown(self.CITY, city)

    def submit(self):
        self.scroll_into_view(self.SUBMIT)
        self.safe_click(self.SUBMIT)

    def submit_succeeded(self):
        return len(self.driver.find_elements(*self.SUCCESS_MODAL)) > 0

    def field_is_invalid(self, field_name):
        """True when the field fails its HTML5 validation constraints."""
        element = self.find(self.FIELDS[field_name])
        return self.driver.execute_script(
            "return !arguments[0].checkValidity();", element)
