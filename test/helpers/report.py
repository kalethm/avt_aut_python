# -*- coding: utf-8 -*-
"""
Generación de reportes al finalizar una corrida de behave.

- behave.json  : salida nativa del formatter json de behave
- cucumber.json: formato compatible con herramientas Cucumber (reportes
                 tipo cucumber-report, ReportPortal, etc.) vía behave2cucumber
- report.html  : reporte HTML generado por behave-html-pretty-formatter
                 (configurado en behave.ini)
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

import config

logger = logging.getLogger(__name__)


def _behave_json_path():
    return Path(config.REPORTS['reports_dir']) / 'behave.json'


def generate_cucumber_report():
    """Convierte behave.json a cucumber.json usando behave2cucumber."""
    src = _behave_json_path()
    dst = Path(config.REPORTS['reports_dir']) / 'cucumber.json'
    if not src.exists() or src.stat().st_size == 0:
        logger.warning('behave.json vacío o inexistente; no se genera cucumber.json')
        return None
    try:
        subprocess.run(
            [sys.executable, '-m', 'behave2cucumber',
             '-i', str(src), '-o', str(dst)],
            check=True, capture_output=True, text=True,
        )
        logger.info('Reporte cucumber.json generado en %s', dst)
        return dst
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        logger.warning('No se pudo generar cucumber.json: %s', exc)
        return None


def summary():
    """Imprime un resumen ejecutivo del behave.json."""
    src = _behave_json_path()
    if not src.exists() or src.stat().st_size == 0:
        return {}
    try:
        with open(src, encoding='utf-8') as fh:
            data = json.load(fh)
    except json.JSONDecodeError:
        return {}

    stats = {'features': 0, 'scenarios': 0, 'steps': 0,
             'passed': 0, 'failed': 0, 'skipped': 0}
    failed = []

    for feature in data:
        stats['features'] += 1
        for element in feature.get('elements', []):
            if element.get('type') != 'scenario':
                continue
            stats['scenarios'] += 1
            status = element.get('status', '')
            stats['passed' if status == 'passed' else
                  'failed' if status == 'failed' else 'skipped'] += 1
            for step in element.get('steps', []):
                stats['steps'] += 1
                if step.get('result', {}).get('status') == 'failed':
                    failed.append(
                        f"{feature.get('name')} :: {element.get('name')} :: "
                        f"{step.get('name')}"
                    )
    return {'stats': stats, 'failed_steps': failed}


def print_summary():
    info = summary()
    if not info:
        return
    s = info['stats']
    logger.info('=' * 60)
    logger.info('RESUMEN: %s features | %s escenarios | %s steps',
                s['features'], s['scenarios'], s['steps'])
    logger.info('  passed=%s failed=%s skipped=%s',
                s['passed'], s['failed'], s['skipped'])
    for item in info['failed_steps']:
        logger.info('  FAIL: %s', item)
    logger.info('=' * 60)
