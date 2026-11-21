# -*- coding: utf-8 -*-
"""
Lectura de datos desde archivos JSON para tests data-driven.

Uso:
    from test.helpers.json_data import load_json, load_rows

    data = load_json('test/data/usuarios.json')
    rows = load_rows('test/data/usuarios.json')
    for row in rows:
        print(row['usuario'], row['clave'])

Los archivos pueden contener un objeto JSON o una lista. load_rows exige una
lista de objetos (equivalente a las filas de un Excel).
"""
import json
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[2]


def load_json(file_path):
    """Carga un archivo JSON y devuelve su contenido (dict o list).

    :param file_path: ruta al .json (relativa al root del proyecto o absoluta)
    :return: contenido parseado del JSON
    """
    path = Path(file_path)
    if not path.is_absolute():
        path = BASE_PATH / path
    if not path.exists():
        raise FileNotFoundError(f'JSON no encontrado: {path}')
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'JSON inválido en {path}: {exc}')


def load_rows(file_path):
    """Carga un JSON que contiene una lista de objetos (data-driven).

    :param file_path: ruta al .json
    :return: list[dict]
    """
    data = load_json(file_path)
    if isinstance(data, dict) and 'rows' in data:
        data = data['rows']
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise ValueError(
            f'{file_path} debe contener una lista de objetos JSON '
            '(o un objeto con clave "rows")')
    return data


def iter_rows(file_path):
    """Iterador sobre las filas como dicts (para scenario outlines)."""
    return iter(load_rows(file_path))
