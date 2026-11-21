# -*- coding: utf-8 -*-
"""
Configuración central del framework de automatización.

Parámetros no sensibles en settings/settings.json. Todo es sobreescribible por
variables de entorno (prefijo QA_) o por un archivo .env.

Precedencia: variable de entorno > settings/settings.json > default.
Los secretos (usuarios, tokens, PINs) solo se leen de .env / entorno.
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_PATH = Path(__file__).absolute().parent
load_dotenv(BASE_PATH / '.env')

SETTINGS_PATH = BASE_PATH / 'settings' / 'settings.json'


def _load_settings():
    """Carga settings/settings.json si existe (parámetros no sensibles)."""
    if not SETTINGS_PATH.exists():
        return {}
    try:
        return json.loads(SETTINGS_PATH.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'settings/settings.json inválido: {exc}')


SETTINGS = _load_settings()


def env(key, default=''):
    """Lee una variable de entorno o .env con fallback al default."""
    value = os.environ.get(key, default)
    return value if value != '' else default


def setting(section, key, default=''):
    """Lee un parámetro de settings/settings.json."""
    return SETTINGS.get(section, {}).get(key, default)


def env_or_setting(env_key, section, key, default=''):
    """Variable de entorno > settings.json > default."""
    value = os.environ.get(env_key)
    if value not in (None, ''):
        return value
    return setting(section, key, default)


def as_bool(value):
    """Convierte bools nativos de JSON o strings de env a bool."""
    if isinstance(value, bool):
        return value
    return str(value).lower() == 'true'


# ============================================================
# API
# ============================================================
API = {
    'base_url': env_or_setting('QA_API_BASE_URL', 'api', 'base_url', 'https://pokeapi.co/api/v2'),
    'timeout': int(env_or_setting('QA_API_TIMEOUT', 'api', 'timeout', 30)),
}

# ============================================================
# Web (Selenium / Playwright)
# ============================================================
WEB = {
    'base_url': env_or_setting('QA_WEB_BASE_URL', 'web', 'base_url', 'https://example.com'),
    'browser': env_or_setting('QA_WEB_BROWSER', 'web', 'browser', 'chrome'),  # chrome | firefox | edge
    'headless': as_bool(env_or_setting('QA_WEB_HEADLESS', 'web', 'headless', False)),
    'implicitly_wait': int(env_or_setting('QA_WEB_IMPLICIT_WAIT', 'web', 'implicitly_wait', 10)),
    'explicitly_wait': int(env_or_setting('QA_WEB_EXPLICIT_WAIT', 'web', 'explicitly_wait', 20)),
}

# ============================================================
# Appium - dispositivos móviles / POS
# ============================================================
# Servidor Appium: local (http://127.0.0.1:4723) o remoto (UFT Digital Lab).
APPIUM = {
    'server_url': env_or_setting('APPIUM_SERVER_URL', 'appium', 'server_url', 'http://127.0.0.1:4723/wd/hub'),
    'platform_name': env_or_setting('APPIUM_PLATFORM_NAME', 'appium', 'platform_name', 'Android'),
    'automation_name': env_or_setting('APPIUM_AUTOMATION_NAME', 'appium', 'automation_name', 'UiAutomator2'),
    'no_reset': as_bool(env_or_setting('APPIUM_NO_RESET', 'appium', 'no_reset', True)),
    'full_reset': as_bool(env_or_setting('APPIUM_FULL_RESET', 'appium', 'full_reset', False)),
    'new_command_timeout': int(env_or_setting('APPIUM_NEW_COMMAND_TIMEOUT', 'appium', 'new_command_timeout', 120)),
}

# ============================================================
# ADB - terminales POS (PAX, Ingenico, Android genéricas)
# ============================================================
ADB = {
    # Ruta al ejecutable adb (por defecto se busca en PATH).
    'path': env_or_setting('ADB_PATH', 'adb', 'path', 'adb'),
    # Tiempo de espera por comando adb en segundos.
    'timeout': int(env_or_setting('ADB_TIMEOUT', 'adb', 'timeout', 30)),
}

# ============================================================
# Dispositivos POS declarados
#
# Cada POS puede usarse por Appium (si el terminal expone UiAutomator2)
# o por ADB directo (input tap/text/keyevent + uiautomator dump).
#
# Campos por dispositivo:
#   name          : nombre lógico usado en los features (ej: "POS_PAX_1")
#   kind          : 'appium' | 'adb' | 'both'
#   manufacturer  : 'pax' | 'ingenico' | 'generic'
#   adb_serial    : serial adb (ej: 'R58N64558ZJ' o '192.168.1.50:5555')
#   udid          : UDID para Appium (normalmente igual al serial)
#   app_package   : package de la app a probar
#   app_activity  : activity de la app a probar
#   unlock_pin    : PIN de desbloqueo Android (opcional)
# ============================================================
POS_DEVICES = {
    'POS_PAX_1': {
        'name': 'POS_PAX_1',
        'kind': env('POS_PAX_1_KIND', 'both'),
        'manufacturer': 'pax',
        'adb_serial': env('POS_PAX_1_ADB_SERIAL', ''),
        'udid': env('POS_PAX_1_UDID', ''),
        'app_package': env('POS_PAX_1_APP_PACKAGE', 'com.getnet.getnetapp'),
        'app_activity': env('POS_PAX_1_APP_ACTIVITY', 'com.coasin.getnetapp.presenter.MainActivity'),
        'unlock_pin': env('POS_PAX_1_UNLOCK_PIN', ''),
    },
    'POS_INGENICO_1': {
        'name': 'POS_INGENICO_1',
        'kind': env('POS_INGENICO_1_KIND', 'both'),
        'manufacturer': 'ingenico',
        'adb_serial': env('POS_INGENICO_1_ADB_SERIAL', ''),
        'udid': env('POS_INGENICO_1_UDID', ''),
        'app_package': env('POS_INGENICO_1_APP_PACKAGE', ''),
        'app_activity': env('POS_INGENICO_1_APP_ACTIVITY', ''),
        'unlock_pin': env('POS_INGENICO_1_UNLOCK_PIN', ''),
    },
}

# Dispositivo POS usado por defecto cuando el feature no especifica uno.
DEFAULT_POS_DEVICE = env('DEFAULT_POS_DEVICE', 'POS_PAX_1')

# ============================================================
# Jira - integración (opcional)
# ============================================================
JIRA = {
    'enabled': as_bool(env_or_setting('JIRA_ENABLED', 'jira', 'enabled', False)),
    'base_url': env_or_setting('JIRA_BASE_URL', 'jira', 'base_url', ''),
    'user': env('JIRA_USER', ''),    # secreto: solo .env / entorno
    'token': env('JIRA_TOKEN', ''),  # secreto: solo .env / entorno
    'project': env_or_setting('JIRA_PROJECT', 'jira', 'project', ''),
    'issue_type': env_or_setting('JIRA_ISSUE_TYPE', 'jira', 'issue_type', 'Bug'),
    'labels': setting('jira', 'labels', []),
    'timeout': int(env_or_setting('JIRA_TIMEOUT', 'jira', 'timeout', 30)),
}

# ============================================================
# ALM / Xray - integración (opcional)
# ============================================================
ALM = {
    'enabled': as_bool(env_or_setting('ALM_ENABLED', 'alm', 'enabled', False)),
    'base_url': env_or_setting('ALM_BASE_URL', 'alm', 'base_url', ''),
    'user': env('ALM_USER', ''),    # secreto: solo .env / entorno
    'token': env('ALM_TOKEN', ''),  # secreto: solo .env / entorno
    'project': env_or_setting('ALM_PROJECT', 'alm', 'project', ''),
    'status_map': setting('alm', 'status_map',
                          {'passed': 1, 'blocked': 2, 'untested': 3,
                           'retest': 4, 'failed': 5}),
    'timeout': int(env_or_setting('ALM_TIMEOUT', 'alm', 'timeout', 30)),
}

# ============================================================
# Reportes
# ============================================================
_output_dir = env_or_setting('REPORT_OUTPUT_DIR', 'reports', 'output_dir', 'output')
if not os.path.isabs(str(_output_dir)):
    _output_dir = str(BASE_PATH / _output_dir)

REPORTS = {
    'output_dir': str(_output_dir),
    'reports_dir': str(Path(_output_dir) / 'reports'),
    'evidencias_dir': str(Path(_output_dir) / 'evidencias'),
    'screenshot_on_failure': as_bool(setting('reports', 'screenshot_on_failure', True)),
    # Generar reporte Cucumber JSON + HTML al finalizar la corrida.
    'cucumber_report': as_bool(setting('reports', 'cucumber_report', True)),
    'html_report': as_bool(setting('reports', 'html_report', True)),
}
