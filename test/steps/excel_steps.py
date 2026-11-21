# -*- coding: utf-8 -*-
"""Steps para tests data-driven con Excel."""
from behave import use_step_matcher, step

from test.helpers.excel_data import load_sheet

use_step_matcher('re')


@step(r"(?:que\s+)?cargo los datos del excel '([^']+)' hoja '([^']+)'")
def step_load_excel(context, file_path, sheet):
    context.excel_rows = load_sheet(file_path, sheet)


@step(r"(?:que\s+)?debo tener (\d+) filas? de datos")
def step_row_count(context, count):
    assert len(context.excel_rows) == int(count), \
        f"Filas encontradas: {len(context.excel_rows)}, esperadas: {count}"


@step(r"(?:que\s+)?cada fila debe tener las claves (.+)")
def step_required_keys(context, keys_text):
    keys = [k.strip().strip("'") for k in keys_text.split(',')]
    for i, row in enumerate(context.excel_rows):
        for key in keys:
            assert key in row, f"Fila {i}: falta la clave '{key}' en {row}"
