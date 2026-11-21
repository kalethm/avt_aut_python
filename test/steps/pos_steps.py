# -*- coding: utf-8 -*-
"""
POS step definitions using raw ADB (no Appium required).

Designed for PAX and Ingenico terminals (Android-based) where Appium/UiAutomator2
is not exposed or is restricted. Uses:
  - input tap / swipe / text / keyevent  -> interactions
  - uiautomator dump                      -> UI validation
  - screencap / logcat                    -> evidence
"""
import logging
import time

from behave import use_step_matcher, step

use_step_matcher("re")

import config
from test.helpers import drivers

logger = logging.getLogger(__name__)


def _adb(context, device=None):
    """Get the AdbClient for a device and mark it as active for evidence."""
    device = device or getattr(context, 'current_device', None) or config.DEFAULT_POS_DEVICE
    context.current_device = device
    return drivers.get_adb_client(device)


# ----------------------------------------------------------------------
# Device lifecycle
# ----------------------------------------------------------------------
@step(r"(?:que\s+)?conecto con el dispositivo POS '([^']+)'")
@step(r"(?:que\s+)?conecto con el POS '([^']+)'")
def step_connect_pos(context, device):
    adb = _adb(context, device)
    assert adb.is_device_connected(), \
        f"ADB device '{device}' (serial={adb.serial or 'default'}) is not connected"
    logger.info("Connected to POS %s (serial=%s)", device, adb.serial or 'default')


@step(r"(?:que\s+)?el dispositivo POS está desbloqueado")
def step_assert_unlocked(context):
    adb = _adb(context)
    output = adb.shell('dumpsys window | grep mDreamingLockscreen')
    logger.info("Lockscreen state: %s", output)


@step(r"(?:que\s+)?desbloqueo el dispositivo con el PIN '([^']+)'")
def step_unlock_pin(context, pin):
    adb = _adb(context)
    pin_cfg = config.POS_DEVICES.get(context.current_device, {}).get('unlock_pin')
    adb.unlock_with_pin(pin or pin_cfg or '')
    logger.info("Unlock PIN sent for %s", context.current_device)


# ----------------------------------------------------------------------
# Interactions
# ----------------------------------------------------------------------
@step(r"(?:que\s+)?hago tap en las coordenadas '(?P<x>\d+)', '(?P<y>\d+)'")
@step(r"(?:que\s+)?tap en coordenadas '(?P<x>\d+)', '(?P<y>\d+)'")
def step_tap(context, x, y):
    _adb(context).tap(int(x), int(y))
    logger.info("Tap (%s, %s) on %s", x, y, context.current_device)


@step(r"(?:que\s+)?deslizo de '(?P<x1>\d+)', '(?P<y1>\d+)' a '(?P<x2>\d+)', '(?P<y2>\d+)'")
@step(r"(?:que\s+)?swipe desde '(?P<x1>\d+)', '(?P<y1>\d+)' hasta '(?P<x2>\d+)', '(?P<y2>\d+)'")
def step_swipe(context, x1, y1, x2, y2):
    _adb(context).swipe(int(x1), int(y1), int(x2), int(y2))


@step(r"(?:que\s+)?ingreso el texto '([^']*)'")
@step(r"(?:que\s+)?input text '([^']*)'")
def step_input_text(context, text):
    _adb(context).input_text(text)


@step(r"(?:que\s+)?presiono la tecla '([^']+)'")
@step(r"(?:que\s+)?presiono keyevent '([^']+)'")
def step_keyevent(context, key):
    _adb(context).keyevent(key)


@step(r"(?:que\s+)?presiono enter")
@step(r"(?:que\s+)?press enter")
def step_press_enter(context):
    _adb(context).press_enter()


# ----------------------------------------------------------------------
# Validations via uiautomator dump
# ----------------------------------------------------------------------
@step(r"(?:que\s+)?la pantalla del POS debe mostrar el texto '([^']+)'")
@step(r"(?:que\s+)?the POS screen should show text '([^']+)'")
def step_assert_text_visible(context, text):
    adb = _adb(context)
    found = adb.is_text_visible(text, timeout=10)
    assert found, f"Text '{text}' not found on screen of {context.current_device}"


@step(r"(?:que\s+)?la pantalla del POS no debe mostrar el texto '([^']+)'")
def step_assert_text_absent(context, text):
    adb = _adb(context)
    found = adb.is_text_visible(text, timeout=3)
    assert not found, f"Text '{text}' should not be visible on {context.current_device}"


@step(r"(?:que\s+)?tomo una captura de pantalla del POS")
@step(r"(?:que\s+)?I take a screenshot of the POS")
def step_screenshot(context):
    adb = _adb(context)
    stamp = time.strftime('%Y%m%d_%H%M%S')
    path = f"{config.REPORTS['output_dir']}/evidencias/{stamp}_{context.current_device}.png"
    adb.screenshot(path)
    logger.info("Screenshot saved: %s", path)


@step(r"(?:que\s+)?la app '([^']+)' está en ejecución")
@step(r"(?:que\s+)?the app '([^']+)' is running")
def step_assert_app_running(context, package):
    adb = _adb(context)
    output = adb.shell(f'pidof {package}')
    assert output.strip(), f"App '{package}' is not running on {context.current_device}"
