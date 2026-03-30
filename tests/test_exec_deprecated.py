#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 mxmilkiib
# SPDX-License-Identifier: GPL-2.0-or-later

"""Regression guard: no .exec_() in the frontend Python files.

Qt6 deprecated QDialog::exec_() in favour of exec().  This test ensures
the pattern cannot be reintroduced silently.
"""

import os

_FRONTEND = os.path.join(os.path.dirname(__file__), '..', 'source', 'frontend')

_CHECKED_FILES = [
    'carla_app.py',
    'carla_host.py',
    'carla_host_control.py',
    'carla_settings.py',
    'carla_shared.py',
    'carla_skin.py',
    'carla_widgets.py',
    'widgets/commondial.py',
    'widgets/paramspinbox.py',
]


def test_no_exec_deprecated():
    offenders = []
    for relpath in _CHECKED_FILES:
        path = os.path.join(_FRONTEND, relpath)
        if not os.path.exists(path):
            continue
        for i, line in enumerate(open(path), 1):
            if '.exec_()' in line and not line.lstrip().startswith('#'):
                offenders.append(f'{relpath}:{i}: {line.rstrip()}')
    assert not offenders, 'Found deprecated .exec_() calls:\n' + '\n'.join(offenders)
