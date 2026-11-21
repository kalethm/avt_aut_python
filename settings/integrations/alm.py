# -*- coding: utf-8 -*-
"""
Cliente ALM genérico (TestRail / Xray-like) para integración con el framework.

Implementa un subconjunto REST compatible con herramientas ALM comunes.
Adapta los endpoints (_request) a tu ALM concreto si es necesario.

Uso:
    from settings.integrations.alm import AlmClient
    alm = AlmClient()
    cases = alm.get_test_cases(project_id=1)

Requiere en .env: ALM_BASE_URL, ALM_USER, ALM_TOKEN, ALM_PROJECT.
"""
import logging

import requests

import config

logger = logging.getLogger(__name__)


class AlmClient:
    """Cliente REST genérico para ALM (estilo TestRail)."""

    def __init__(self, base_url=None, user=None, token=None, timeout=None):
        self.base_url = (base_url or config.ALM['base_url']).rstrip('/')
        self.user = user or config.ALM['user']
        self.token = token or config.ALM['token']
        self.timeout = timeout or config.ALM['timeout']
        if not all([self.base_url, self.user, self.token]):
            raise RuntimeError(
                'ALM no está configurado. Define ALM_BASE_URL, ALM_USER '
                'y ALM_TOKEN en .env o config.py.'
            )

    def _request(self, method, path, **kwargs):
        url = f'{self.base_url}/index.php?/api/v2{path}'
        resp = requests.request(
            method, url,
            auth=(self.user, self.token),
            headers={'Content-Type': 'application/json'},
            timeout=self.timeout,
            **kwargs,
        )
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    # ---------------------------------------------------------
    def get_projects(self):
        return self._request('GET', '/get_projects')

    def get_test_cases(self, project_id):
        return self._request('GET', f'/get_cases/{project_id}')

    def get_test_runs(self, project_id):
        return self._request('GET', f'/get_runs/{project_id}')

    def add_result(self, run_id, case_id, status_id,
                   comment='', elapsed=None):
        """Publica el resultado de un caso en un run (status_id: 1=passed, 2=blocked, 3=untested, 4=retest, 5=failed)."""
        payload = {
            'status_id': status_id,
            'comment': comment,
            'elapsed': elapsed or '1m',
        }
        return self._request('POST', f'/add_result_for_case/{run_id}/{case_id}',
                             json=payload)
