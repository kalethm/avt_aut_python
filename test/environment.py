# -*- coding: utf-8 -*-
"""
Behave environment hooks: driver lifecycle, evidence on failure.
"""
import logging
import os
from datetime import datetime

from behave import use_step_matcher

import config
from test.helpers import drivers

logger = logging.getLogger(__name__)
use_step_matcher("re")


def before_all(context):
    """Initialize shared resources before the whole run."""
    os.makedirs(config.REPORTS['output_dir'], exist_ok=True)
    os.makedirs(config.REPORTS['reports_dir'], exist_ok=True)
    os.makedirs(config.REPORTS['evidencias_dir'], exist_ok=True)
    context.api = drivers.ApiClient()
    context.current_device = None
    context.run_results = []
    logger.info("Run started. Output dir: %s", config.REPORTS['output_dir'])


def before_scenario(context, scenario):
    """Reset per-scenario state."""
    context.current_device = None
    context.scenario_name = scenario.name


def _report_failure_to_jira(context, scenario, evidence_paths):
    """Create a Jira bug for a failed scenario.

    Config lives in settings/integrations/jira.py (ENABLED, PROJECT...).
    """
    from settings.integrations import jira as jira_settings
    if not jira_settings.ENABLED:
        return
    try:
        jira = jira_settings.JiraClient()
        errors = '\n'.join(
            s.error_message or '' for s in scenario.steps
            if s.status.name == 'failed') or 'Sin detalle de error.'
        description = (
            f"Feature: {scenario.feature.name}\n"
            f"Escenario: {scenario.name}\n"
            f"Tags: {', '.join(scenario.tags)}\n\n"
            f"Error:\n{errors}")
        issue_key = jira.create_issue(
            summary=f"[QA Auto] Falla: {scenario.name}",
            description=description)
        context.jira_issue = issue_key
        for path in evidence_paths:
            try:
                jira.add_attachment(issue_key, path)
            except Exception as exc:  # noqa: BLE001
                logger.warning("No se pudo adjuntar %s al issue: %s", path, exc)
        logger.info("Bug creado en Jira: %s", issue_key)
    except Exception as exc:  # noqa: BLE001
        logger.warning("No se pudo crear el issue en Jira: %s", exc)


def _create_test_execution(context):
    """Create a Jira 'Test Execution' issue with the run results.

    Linked to the TEST_PLAN configured in settings/integrations/jira.json.
    """
    from settings.integrations import jira as jira_settings
    results = getattr(context, 'run_results', [])
    if not jira_settings.ENABLED or not jira_settings.TEST_PLAN or not results:
        return
    try:
        jira = jira_settings.JiraClient()
        stamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        passed = sum(1 for r in results if r['status'] == 'passed')
        failed = len(results) - passed
        lines = '\n'.join(
            f"- {'PASS' if r['status'] == 'passed' else 'FAIL'}: {r['name']}"
            for r in results)
        description = (
            f"Ejecucion automatica (behave) - {stamp}\n\n"
            f"Resultado: {passed} passed, {failed} failed\n\n{lines}")
        exec_key = jira.create_issue(
            summary=f"[Test Execution] {jira_settings.TEST_PLAN} - {stamp}",
            description=description,
            issue_type='Tarea',
            labels=['qa-automation', 'test-execution'])
        jira.link_issues(exec_key, jira_settings.TEST_PLAN)
        logger.info("Test Execution creado en Jira: %s", exec_key)
    except Exception as exc:  # noqa: BLE001
        logger.warning("No se pudo crear el Test Execution en Jira: %s", exc)


def after_scenario(context, scenario):
    """Attach a screenshot as evidence when the scenario fails."""
    context.run_results.append(
        {'name': scenario.name, 'status': scenario.status.name})
    if scenario.status.name != 'failed':
        return

    evidence_dir = os.path.join(config.REPORTS['output_dir'], 'evidencias')
    os.makedirs(evidence_dir, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    evidence_paths = []

    # Web driver screenshot
    for browser, driver in drivers.WebDriverManager._instances.items():
        try:
            path = os.path.join(evidence_dir, f'{stamp}_{scenario.name}_{browser}.png')
            driver.save_screenshot(path)
            evidence_paths.append(path)
            scenario.attach(open(path, 'rb').read(), 'image/png',
                            f'screenshot {browser}')
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not capture web screenshot: %s", exc)

    # Appium driver screenshot
    for device, driver in drivers._drivers.items():
        try:
            png = driver.get_screenshot_as_png()
            path = os.path.join(evidence_dir, f'{stamp}_{scenario.name}_{device}.png')
            with open(path, 'wb') as fh:
                fh.write(png)
            evidence_paths.append(path)
            scenario.attach(png, 'image/png', f'screenshot {device}')
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not capture appium screenshot for %s: %s", device, exc)

    # ADB screenshot for the active POS device
    if context.current_device:
        try:
            adb = drivers.get_adb_client(context.current_device)
            path = os.path.join(evidence_dir, f'{stamp}_{scenario.name}_{context.current_device}.png')
            adb.screenshot(path)
            evidence_paths.append(path)
            scenario.attach(open(path, 'rb').read(), 'image/png',
                            f'screenshot {context.current_device}')
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not capture adb screenshot: %s", exc)

    _report_failure_to_jira(context, scenario, evidence_paths)


def after_all(context):
    """Publish the run results to Jira and close all drivers/sessions."""
    _create_test_execution(context)
    drivers.quit_all()
