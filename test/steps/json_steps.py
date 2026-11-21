# -*- coding: utf-8 -*-
"""Steps para tests data-driven con archivos JSON."""
from behave import use_step_matcher, step

from test.helpers.json_data import load_json, load_rows

use_step_matcher('re')


@step(r"(?:que\s+)?cargo los datos del json '([^']+)'")
def step_load_json(context, file_path):
    context.json_data = load_json(file_path)


@step(r"(?:que\s+)?cargo las filas del json '([^']+)'")
def step_load_json_rows(context, file_path):
    context.json_rows = load_rows(file_path)


@step(r"(?:que\s+)?debo tener (\d+) filas? de datos en el json")
def step_json_row_count(context, count):
    assert len(context.json_rows) == int(count), \
        f"Filas encontradas: {len(context.json_rows)}, esperadas: {count}"


@step(r"(?:que\s+)?cada fila del json debe tener las claves (.+)")
def step_json_required_keys(context, keys_text):
    keys = [k.strip().strip("'") for k in keys_text.split(',')]
    for i, row in enumerate(context.json_rows):
        for key in keys:
            assert key in row, f"Fila {i}: falta la clave '{key}' en {row}"


@step(r"(?:que\s+)?el json debe contener la clave '([^']+)'")
def step_json_has_key(context, key):
    assert key in context.json_data, \
        f"Clave '{key}' no encontrada en {context.json_data}"
