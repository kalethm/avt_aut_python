# -*- coding: utf-8 -*-
"""
Lectura de datos desde Excel para tests data-driven.

Uso:
    from test.helpers.excel_data import load_sheet, iter_rows

    rows = load_sheet('test/data/usuarios.xlsx', sheet='usuarios')
    for row in rows:
        print(row['usuario'], row['clave'])

La primera fila de la hoja se toma como encabezado (nombres de columna).
"""
from pathlib import Path

from openpyxl import load_workbook

BASE_PATH = Path(__file__).resolve().parents[2]


def load_sheet(file_path, sheet=0):
    """Carga una hoja de Excel y devuelve una lista de dicts.

    :param file_path: ruta al .xlsx (relativa al root del proyecto o absoluta)
    :param sheet: nombre de la hoja o índice (0-based)
    :return: list[dict] con las filas de datos
    """
    path = Path(file_path)
    if not path.is_absolute():
        path = BASE_PATH / path
    if not path.exists():
        raise FileNotFoundError(f'Excel no encontrado: {path}')

    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet] if isinstance(sheet, str) else wb.worksheets[sheet]

    rows_iter = ws.iter_rows(values_only=True)
    headers = [str(h).strip() if h is not None else f'col_{i}'
               for i, h in enumerate(next(rows_iter, ()))]

    data = []
    for values in rows_iter:
        if all(v is None for v in values):
            continue
        data.append({h: v for h, v in zip(headers, values)})
    wb.close()
    return data


def iter_rows(file_path, sheet=0):
    """Iterador sobre las filas como dicts (para scenario outlines)."""
    return iter(load_sheet(file_path, sheet))
