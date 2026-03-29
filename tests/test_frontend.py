#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 mxmilkiib
# SPDX-License-Identifier: GPL-2.0-or-later

"""Minimal smoke tests for the Carla Python frontend.

Run with:  pytest tests/test_frontend.py  (from repo root)
Or:        make check  (covers syntax + UI import)
"""

import importlib.util
import os
import sys

FRONTEND = os.path.join(os.path.dirname(__file__), '..', 'source', 'frontend')
BIN      = os.path.join(os.path.dirname(__file__), '..', 'bin')

sys.path.insert(0, os.path.abspath(FRONTEND))
sys.path.insert(0, os.path.abspath(BIN))


def _load(relpath):
    path = os.path.join(FRONTEND, relpath)
    spec = importlib.util.spec_from_file_location(relpath.replace('/', '.'), path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_carla_shared_imports():
    mod = _load('carla_shared.py')
    assert hasattr(mod, 'CARLA_KEY_MAIN_PROJECT_FOLDER')
    assert hasattr(mod, 'CARLA_DEFAULT_MAIN_PROJECT_FOLDER')


def test_main_and_canvas_keys_have_defaults():
    """MAIN_ and CANVAS_ settings keys must each have a matching CARLA_DEFAULT_*.
    ENGINE/PATHS/OSC/WINE/EXPERIMENTAL keys intentionally lack defaults in
    carla_shared (they come from engine detection at runtime)."""
    mod = _load('carla_shared.py')
    keys     = [n for n in dir(mod) if n.startswith('CARLA_KEY_MAIN_')
                                    or n.startswith('CARLA_KEY_CANVAS_')]
    defaults = {n for n in dir(mod) if n.startswith('CARLA_DEFAULT_')}
    missing  = []
    for key in keys:
        suffix  = key[len('CARLA_KEY_'):]
        default = 'CARLA_DEFAULT_' + suffix
        if default not in defaults:
            missing.append(f'{key} -> {default}')
    assert not missing, 'Keys without matching defaults:\n' + '\n'.join(missing)


def test_ui_carla_host_importable():
    ui_path = os.path.join(FRONTEND, 'ui_carla_host.py')
    if not os.path.exists(ui_path):
        import pytest
        pytest.skip('ui_carla_host.py not generated yet (run make generate-ui)')
    mod = _load('ui_carla_host.py')
    assert hasattr(mod, 'Ui_CarlaHostW')


def test_ui_carla_settings_has_default_project_widgets():
    ui_path = os.path.join(FRONTEND, 'ui_carla_settings.py')
    if not os.path.exists(ui_path):
        import pytest
        pytest.skip('ui_carla_settings.py not generated yet (run make generate-ui)')
    content = open(ui_path).read()
    assert 'le_main_default_project' in content,     'Missing le_main_default_project in generated settings UI'
    assert 'b_main_default_project_open' in content, 'Missing b_main_default_project_open in generated settings UI'
