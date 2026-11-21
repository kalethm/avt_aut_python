# -*- coding: utf-8 -*-
"""
API step definitions (requests-based).
"""
import logging

from behave import use_step_matcher, step

use_step_matcher("re")

import config

logger = logging.getLogger(__name__)


@step(r"(?:que\s+)?preparo la petición URI '([^']+)' con path '([^']+)'")
@step(r"(?:que\s+)?prepare request uri '([^']+)' with path '([^']+)'")
def step_prepare_uri(context, uri, path):
    context.request_url = f"{uri.rstrip('/')}/{path.lstrip('/')}"
    logger.info("Request URL: %s", context.request_url)


@step(r"(?:que\s+)?preparo el método de la petición '([^']+)'")
@step(r"(?:que\s+)?prepare request method '([^']+)'")
def step_prepare_method(context, method):
    context.request_method = method.upper()


@step(r"(?:que\s+)?preparo los headers de la petición")
@step(r"(?:que\s+)?prepare request headers")
def step_prepare_headers(context):
    context.request_headers = getattr(context, 'request_headers', {})
    context.request_headers.setdefault('Accept', 'application/json')


@step(r"(?:que\s+)?preparo el body de la petición")
@step(r"(?:que\s+)?prepare request body")
def step_prepare_body(context):
    context.request_body = getattr(context, 'request_body', None)


@step(r"(?:que\s+)?envío la petición")
@step(r"(?:que\s+)?send request")
def step_send_request(context):
    kwargs = {}
    if hasattr(context, 'request_headers'):
        kwargs['headers'] = context.request_headers
    if hasattr(context, 'request_body') and context.request_body is not None:
        kwargs['json'] = context.request_body
    response = context.api.request(
        getattr(context, 'request_method', 'GET'),
        getattr(context, 'request_url'),
        **kwargs,
    )
    logger.info("Response %s - %s", response.status_code, response.url)


@step(r"(?:que\s+)?el código de estado debe ser '([^']+)'")
@step(r"(?:que\s+)?verify status code is '([^']+)'")
def step_verify_status(context, expected):
    actual = context.api.last_response.status_code
    assert str(actual) == str(expected), f"Expected status {expected}, got {actual}"


@step(r"(?:que\s+)?la respuesta JSON debe contener la clave '([^']+)'")
@step(r"(?:que\s+)?verify json response contains key '([^']+)'")
def step_verify_json_key(context, key):
    data = context.api.last_response.json()
    assert key in data, f"Key '{key}' not found in response: {data}"


@step(r"(?:que\s+)?el valor JSON de la clave '([^']+)' debe ser de tipo '([^']+)'")
@step(r"(?:que\s+)?verify json response value of the key '([^']+)' is of type '([^']+)'")
def step_verify_json_type(context, key, expected_type):
    data = context.api.last_response.json()
    assert key in data, f"Key '{key}' not found in response"
    value = data[key]
    type_map = {'str': str, 'int': int, 'float': float, 'bool': bool, 'list': list, 'dict': dict}
    py_type = type_map.get(expected_type)
    assert py_type and isinstance(value, py_type), \
        f"Key '{key}' expected type {expected_type}, got {type(value).__name__}: {value!r}"


@step(r"(?:que\s+)?la respuesta debe contener el valor '([^']+)'")
@step(r"(?:que\s+)?verify response contains value '([^']+)'")
def step_verify_contains(context, value):
    assert value in context.api.last_response.text, \
        f"Value '{value}' not found in response"
