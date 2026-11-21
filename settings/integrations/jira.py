# -*- coding: utf-8 -*-
"""
Cliente Jira (REST API v3) + configuración de la integración.

Toda la configuración vive en settings/integrations/jira.json. Los
secretos (user/token) pueden dejarse vacíos en el JSON y definirse en
.env (JIRA_USER / JIRA_TOKEN) para no subirlos al repositorio.

Uso:
    from settings.integrations.jira import JiraClient
    jira = JiraClient()
    issue = jira.create_issue('QA', 'Bug en login', 'Descripción...')
"""
import logging
from pathlib import Path

import requests

import config
from test.helpers.json_data import load_json

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).with_name('jira.json')

# Configuración de la integración: se edita en jira.json (mismo dir).
_cfg = load_json(CONFIG_PATH) if CONFIG_PATH.exists() else {}

ENABLED = _cfg.get('enabled', False)
BASE_URL = _cfg.get('base_url', '')
PROJECT = _cfg.get('project', '')
ISSUE_TYPE = _cfg.get('issue_type', 'Bug')
LABELS = _cfg.get('labels', [])
TIMEOUT = _cfg.get('timeout', 30)
USER = _cfg.get('user', '')      # si está vacío se usa JIRA_USER del .env
TOKEN = _cfg.get('token', '')    # si está vacío se usa JIRA_TOKEN del .env
TEST_PLAN = _cfg.get('test_plan', '')  # key del Test Plan al que enlazar ejecuciones


class JiraClient:
    """Cliente mínimo de Jira Cloud / Server (REST API v3)."""

    def __init__(self, base_url=None, user=None, token=None, timeout=None):
        self.base_url = (base_url or BASE_URL or config.JIRA['base_url']).rstrip('/')
        self.user = user or USER or config.JIRA['user']
        self.token = token or TOKEN or config.JIRA['token']
        self.timeout = timeout or TIMEOUT or config.JIRA['timeout']
        if not all([self.base_url, self.user, self.token]):
            raise RuntimeError(
                'Jira no está configurado. Define "user" y "token" en '
                'settings/integrations/jira.json o JIRA_USER/JIRA_TOKEN en .env.'
            )

    def _request(self, method, path, **kwargs):
        url = f'{self.base_url}/rest/api/3{path}'
        resp = requests.request(
            method, url,
            auth=(self.user, self.token),
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'},
            timeout=self.timeout,
            **kwargs,
        )
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    # ---------------------------------------------------------
    def create_issue(self, project=None, summary='', description='',
                     issue_type=None, labels=None, parent_key=None):
        """Crea un issue y devuelve su key (ej: 'QA-123').

        :param parent_key: si se indica, crea el issue como subtarea de esa key.
        """
        fields = {
            'project': {'key': project or PROJECT},
            'summary': summary,
            'description': {
                'type': 'doc', 'version': 1,
                'content': [{'type': 'paragraph',
                             'content': [{'type': 'text',
                                          'text': description}]}],
            },
            'issuetype': {'name': issue_type or ISSUE_TYPE},
            'labels': labels if labels is not None else LABELS,
        }
        if parent_key:
            fields['parent'] = {'key': parent_key}
            fields['issuetype'] = {'name': 'Subtarea'}
        data = self._request('POST', '/issue', json={'fields': fields})
        logger.info('Jira issue creado: %s', data.get('key'))
        return data.get('key')

    def link_issues(self, inward_key, outward_key, link_type='Relates'):
        """Enlaza dos issues (ej: un Test Execution con su Test Plan)."""
        payload = {
            'type': {'name': link_type},
            'inwardIssue': {'key': inward_key},
            'outwardIssue': {'key': outward_key},
        }
        return self._request('POST', '/issueLink', json=payload)

    def add_comment(self, issue_key, comment):
        """Agrega un comentario a un issue."""
        payload = {
            'body': {
                'type': 'doc', 'version': 1,
                'content': [{'type': 'paragraph',
                             'content': [{'type': 'text',
                                          'text': comment}]}],
            }
        }
        return self._request('POST', f'/issue/{issue_key}/comment', json=payload)

    def get_issue(self, issue_key):
        """Obtiene los campos de un issue."""
        return self._request('GET', f'/issue/{issue_key}?fields=summary,status')

    def add_attachment(self, issue_key, file_path):
        """Adjunta un archivo al issue (ej: screenshot de evidencia)."""
        url = f'{self.base_url}/rest/api/3/issue/{issue_key}/attachments'
        with open(file_path, 'rb') as fh:
            resp = requests.post(
                url,
                auth=(self.user, self.token),
                headers={'X-Atlassian-Token': 'no-check'},
                files={'file': fh},
                timeout=self.timeout,
            )
        resp.raise_for_status()
        return resp.json()

    def search(self, jql, max_results=50):
        """Ejecuta un JQL y devuelve los issues encontrados."""
        data = self._request(
            'POST', '/search/jql',
            json={'jql': jql, 'maxResults': max_results},
        )
        return data.get('issues', [])
