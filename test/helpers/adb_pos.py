# -*- coding: utf-8 -*-
"""
ADB wrapper for POS terminals (PAX, Ingenico and generic Android devices).

Wraps `adb` CLI commands: device listing, tap/swipe/keyevent/text input and
UI hierarchy dumps (uiautomator) for validation without Appium.
"""
import logging
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger(__name__)


class AdbError(Exception):
    pass


class AdbClient:
    """Client to execute adb commands against a POS terminal."""

    def __init__(self, serial: str = '', timeout: Optional[int] = None):
        """
        Args:
            serial: adb serial of the device (e.g. 'R58N64558ZJ' or
                '192.168.1.50:5555'). Empty = default device (adb without -s).
            timeout: command timeout in seconds.
        """
        self.serial = serial
        self.timeout = timeout or config.ADB['timeout']
        self.adb = config.ADB['path']

    # ------------------------------------------------------------------
    # Core command execution
    # ------------------------------------------------------------------
    def _cmd(self, *args, check: bool = True) -> subprocess.CompletedProcess:
        cmd = [self.adb]
        if self.serial:
            cmd += ['-s', self.serial]
        cmd += list(args)
        logger.debug("ADB> %s", ' '.join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
        if check and result.returncode != 0:
            raise AdbError(
                f"adb {' '.join(args)} failed ({result.returncode}): {result.stderr.strip()}"
            )
        return result

    # ------------------------------------------------------------------
    # Device state
    # ------------------------------------------------------------------
    def devices(self) -> list:
        """Return list of connected adb devices as (serial, state) tuples."""
        result = self._cmd('devices')
        devices = []
        for line in result.stdout.splitlines()[1:]:
            parts = line.split()
            if len(parts) == 2:
                devices.append((parts[0], parts[1]))
        return devices

    def is_device_connected(self) -> bool:
        if not self.serial:
            return len(self.devices()) > 0
        return any(s == self.serial and state == 'device' for s, state in self.devices())

    def shell(self, command: str, check: bool = True) -> str:
        """Execute a shell command on the device and return stdout."""
        result = self._cmd('shell', command, check=check)
        return result.stdout.strip()

    # ------------------------------------------------------------------
    # Input actions (POS terminals are usually touch + keypad)
    # ------------------------------------------------------------------
    def tap(self, x: int, y: int) -> None:
        self.shell(f'input tap {x} {y}')

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
        self.shell(f'input swipe {x1} {y1} {x2} {y2} {duration_ms}')

    def input_text(self, text: str) -> None:
        """Type text. Spaces must be %s for `input text`."""
        escaped = text.replace(' ', '%s')
        self.shell(f'input text "{escaped}"')

    def keyevent(self, keycode: str | int) -> None:
        """Send a keyevent (e.g. 'KEYCODE_ENTER', 'KEYCODE_BACK' or numeric)."""
        self.shell(f'input keyevent {keycode}')

    def press_enter(self) -> None:
        self.keyevent('KEYCODE_ENTER')

    def press_back(self) -> None:
        self.keyevent('KEYCODE_BACK')

    def press_home(self) -> None:
        self.keyevent('KEYCODE_HOME')

    def press_power(self) -> None:
        self.keyevent('KEYCODE_POWER')

    def wake_screen(self) -> None:
        self.shell('input keyevent KEYCODE_WAKEUP')

    # ------------------------------------------------------------------
    # PIN / unlock helpers
    # ------------------------------------------------------------------
    def unlock_with_pin(self, pin: str, delay_ms: int = 150) -> None:
        """
        Basic PIN unlock flow for Android POS terminals:
        wake screen -> swipe up (or enter) -> type PIN -> enter.
        """
        self.wake_screen()
        time.sleep(1)
        # Most POS lock screens accept swipe up or direct PIN entry.
        self.swipe(540, 1800, 540, 600, 200)
        time.sleep(0.5)
        for digit in pin:
            self.keyevent(f'KEYCODE_{digit}')
            time.sleep(delay_ms / 1000)
        self.press_enter()

    # ------------------------------------------------------------------
    # UI hierarchy (uiautomator dump)
    # ------------------------------------------------------------------
    def ui_dump(self, remote_path: str = '/sdcard/window_dump.xml',
                local_path: Optional[str] = None) -> str:
        """
        Dump the current UI hierarchy via `uiautomator dump` and return the XML.

        Args:
            remote_path: path on the device where the dump is written.
            local_path: optional local path to pull the dump to.

        Returns:
            UI hierarchy XML as string.
        """
        self.shell(f'uiautomator dump {remote_path}')
        if local_path:
            self._cmd('pull', remote_path, local_path)
            return Path(local_path).read_text(encoding='utf-8', errors='replace')
        return self.shell(f'cat {remote_path}')

    def find_nodes_by_text(self, text: str, xml: Optional[str] = None) -> list:
        """
        Find UI nodes containing the given text in the current dump.

        Returns:
            List of dicts with node attributes (text, resource-id, bounds, ...).
        """
        xml = xml or self.ui_dump()
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            logger.warning("UI dump XML could not be parsed")
            return []
        matches = []
        for node in root.iter('node'):
            node_text = node.get('text', '')
            if text.lower() in node_text.lower():
                matches.append(dict(node.attrib))
        return matches

    def is_text_visible(self, text: str, timeout: int = 10, poll: float = 0.5) -> bool:
        """Poll the UI dump until `text` appears or timeout expires."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.find_nodes_by_text(text):
                return True
            time.sleep(poll)
        return False

    # ------------------------------------------------------------------
    # Screenshots / logs
    # ------------------------------------------------------------------
    def screenshot(self, local_path: str) -> str:
        remote = '/sdcard/qa_screenshot.png'
        self.shell(f'screencap -p {remote}')
        self._cmd('pull', remote, local_path)
        return local_path

    def logcat(self, lines: int = 200) -> str:
        return self.shell(f'logcat -d -t {lines}')
