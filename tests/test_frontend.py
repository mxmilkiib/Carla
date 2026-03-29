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


# ----------------------------------------------------------------------------
# Settings key coverage in carla_host.py fSavedSettings dict
# ----------------------------------------------------------------------------

def _host_source():
    return open(os.path.join(FRONTEND, 'carla_host.py')).read()

def _settings_source():
    return open(os.path.join(FRONTEND, 'carla_settings.py')).read()


def test_fsavedsettings_contains_main_keys():
    """Every CARLA_KEY_MAIN_* constant must appear in carla_host.py's
    fSavedSettings dict so it is available at runtime."""
    shared  = _load('carla_shared.py')
    host_src = _host_source()
    keys    = [n for n in dir(shared) if n.startswith('CARLA_KEY_MAIN_')]
    missing = [k for k in keys if k not in host_src]
    assert not missing, 'MAIN keys absent from carla_host.py:\n' + '\n'.join(missing)


def test_settings_load_save_reset_cover_default_project():
    """CARLA_KEY_MAIN_DEFAULT_PROJECT must appear in the load, save, and reset
    paths of carla_settings.py."""
    src = _settings_source()
    key = 'CARLA_KEY_MAIN_DEFAULT_PROJECT'
    assert src.count(key) >= 3, (
        f'{key} should appear at least 3 times in carla_settings.py '
        f'(import, loadSettings, saveSettings/resetSettings); found {src.count(key)}'
    )


# ----------------------------------------------------------------------------
# Feature-branch regression tests (source scanning, no display needed)
# ----------------------------------------------------------------------------

def _src(relpath):
    return open(os.path.join(FRONTEND, relpath)).read()


def test_file_open_validates_project_folder():
    """slot_fileOpen must validate the project folder before passing it to
    the dialog (bugfix/file-open-default-folder)."""
    src = _src('carla_host.py')
    assert 'os.path.isdir' in src, \
        'slot_fileOpen is missing os.path.isdir validation for project folder'


def test_default_session_startup_reads_key():
    """Startup path must reference CARLA_KEY_MAIN_DEFAULT_PROJECT so the
    default project is loaded when no CLI argument is given."""
    src = _src('carla_host.py')
    assert 'CARLA_KEY_MAIN_DEFAULT_PROJECT' in src, \
        'carla_host.py startup path missing CARLA_KEY_MAIN_DEFAULT_PROJECT check'
    assert 'os.path.isfile' in src, \
        'carla_host.py startup path missing os.path.isfile guard for default project'


def test_canvas_autosize_expands_scene_rect():
    """restoreGroupPositions must expand the scene rect to fit all restored
    items (feature/patchbay-canvas-autosize)."""
    src = _src('patchcanvas/patchcanvas.py')
    assert 'itemsBoundingRect' in src, \
        'patchcanvas.py missing itemsBoundingRect call for canvas autosize'
    assert 'united' in src, \
        'patchcanvas.py missing united() call to expand scene rect'


def test_drag_scroll_in_scene():
    """mouseMoveEvent must contain auto-scroll logic when the cursor is near
    the viewport edge (feature/patchbay-drag-scroll)."""
    src = _src('patchcanvas/scene.py')
    assert 'hbar.setValue' in src, \
        'scene.py missing hbar.setValue auto-scroll in mouseMoveEvent'
    assert 'vbar.setValue' in src, \
        'scene.py missing vbar.setValue auto-scroll in mouseMoveEvent'


# ----------------------------------------------------------------------------
# Patchcanvas and widget module imports
# ----------------------------------------------------------------------------

def test_patchcanvas_modules_importable():
    import importlib
    for modname in (
        'patchcanvas',
        'patchcanvas.patchcanvas',
        'patchcanvas.scene',
        'patchcanvas.theme',
        'patchcanvas.utils',
    ):
        importlib.import_module(modname)


def test_widget_modules_importable():
    import importlib
    for modname in (
        'widgets.commondial',
        'widgets.digitalpeakmeter',
        'widgets.pixmapdial',
        'widgets.paramspinbox',
        'widgets.ledbutton',
    ):
        importlib.import_module(modname)


def test_utils_module_importable():
    _load('utils/qsafesettings.py')
