# -*- coding: utf-8 -*-
"""
Step definitions for the DemoQA Student Registration Form (Practice Form).

Data comes from a JSON file (settings/data/*.json) loaded through
test.helpers.json_data; locators live in test.pages.practice_form_page.
"""
import logging

from behave import use_step_matcher, step

use_step_matcher("re")

from test.helpers.json_data import load_json
from test.pages.practice_form_page import PracticeFormPage

logger = logging.getLogger(__name__)


@step(r"(?:que\s+)?abro el formulario de registro de estudiantes")
def step_open_practice_form(context):
    context.practice_form = PracticeFormPage().open()


@step(r"(?:que\s+)?completo el formulario con los datos del json '([^']+)'")
def step_fill_practice_form(context, file_path):
    data = load_json(file_path)
    context.student_data = data['estudiante']
    context.expected_result = data.get('resultado_esperado', {})
    logger.info("Filling practice form for %s %s",
                context.student_data['first_name'],
                context.student_data['last_name'])
    context.practice_form.fill_form(context.student_data)


@step(r"(?:que\s+)?envío el formulario de registro")
def step_submit_practice_form(context):
    context.practice_form.submit()


@step(r"(?:que\s+)?el campo '([^']+)' se marca como inválido")
def step_field_is_invalid(context, field_name):
    assert context.practice_form.field_is_invalid(field_name), \
        f"El campo '{field_name}' debería ser inválido y no lo es"


@step(r"(?:que\s+)?el campo '([^']+)' se marca como válido")
def step_field_is_valid(context, field_name):
    assert not context.practice_form.field_is_invalid(field_name), \
        f"El campo '{field_name}' debería ser válido y no lo es"


@step(r"(?:que\s+)?el formulario no se envía")
def step_form_not_submitted(context):
    assert not context.practice_form.submit_succeeded(), \
        "El formulario se envió pero se esperaba un error de validación"


@step(r"(?:que\s+)?el formulario se envía correctamente")
def step_form_submitted(context):
    assert context.practice_form.submit_succeeded(), \
        "El formulario no se envió (no apareció el modal de confirmación)"
