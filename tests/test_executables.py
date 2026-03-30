#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 mxmilkiib
# SPDX-License-Identifier: GPL-2.0-or-later

"""Startup smoke tests for every Carla Python frontend executable.

Each script is launched with QT_QPA_PLATFORM=offscreen and killed after a
short timeout.  The test fails if any Python Traceback or TypeError appears
in the startup output, indicating a runtime error before the event loop
settles.

Run with:  pytest tests/test_executables.py -v   (from repo root)
Or:        make test
"""

import os
import subprocess
import sys
import threading
import time

_REPO    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_FRONT   = os.path.join(_REPO, 'source', 'frontend')
_BIN     = os.path.join(_REPO, 'bin')

# seconds to let each script initialise before we kill it
_STARTUP_WINDOW = 2.0

_ENV = {
    **os.environ,
    'QT_QPA_PLATFORM':  'offscreen',
    'PYTHONPATH':        f'{_FRONT}:{_BIN}',
    # suppress glib/dbus noise that isn't relevant
    'DBUS_SESSION_BUS_ADDRESS': 'disabled:',
}

# (script name, tolerated non-traceback patterns on stderr/stdout)
_SCRIPTS = [
    'carla-plugin-patchbay',
    'carla-plugin',
    'carla-patchbay',
    'carla-rack',
    'carla',
    'carla-jack-single',
    'carla-jack-multi',
    # carla-control, carla-rest-frontend: need extra network/OSC setup; skip
]


def _collect_output(script: str, window: float) -> str:
    """Launch script, collect combined stdout+stderr for `window` seconds, then kill."""
    path = os.path.join(_FRONT, script)
    proc = subprocess.Popen(
        [sys.executable, path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=_ENV,
        text=True,
    )
    lines = []

    def _reader():
        for line in proc.stdout:
            lines.append(line)

    t = threading.Thread(target=_reader, daemon=True)
    t.start()
    t.join(timeout=window)

    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    # drain any remaining buffered lines after termination
    t.join(timeout=1)
    return ''.join(lines)


def _assert_no_traceback(script: str, output: str):
    tb_lines = [l.rstrip() for l in output.splitlines()
                if 'Traceback (most recent call last)' in l]
    assert not tb_lines, (
        f'{script}: Python exception(s) during startup:\n'
        + '\n'.join(tb_lines[:5])
        + '\n\n--- startup output ---\n' + output[:2000]
    )


# ---------------------------------------------------------------------------
# One test per executable
# ---------------------------------------------------------------------------

def _make_test(name):
    def test_fn():
        out = _collect_output(name, _STARTUP_WINDOW)
        _assert_no_traceback(name, out)
    test_fn.__name__ = f'test_startup_{name.replace("-", "_")}'
    test_fn.__doc__  = f'Smoke-test: {name} must start without Python tracebacks'
    return test_fn


for _script in _SCRIPTS:
    _fn = _make_test(_script)
    globals()[_fn.__name__] = _fn
