#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 mxmilkiib
# SPDX-License-Identifier: GPL-2.0-or-later

"""UI tests for the Carla settings dialog and related widgets.

Requires no real display — runs under the Qt offscreen platform.
Run with:  pytest tests/test_ui.py -v
"""

import os
import sys

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

# Add frontend and bin to path before any Qt import
_REPO = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(os.path.join(_REPO, 'source', 'frontend')))
sys.path.insert(0, os.path.abspath(os.path.join(_REPO, 'bin')))

import pytest
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# One QApplication for the whole test session
# ---------------------------------------------------------------------------

@pytest.fixture(scope='session')
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


# ---------------------------------------------------------------------------
# Minimal host mock that satisfies CarlaSettingsW.__init__ + loadSettings
# ---------------------------------------------------------------------------

def _make_host():
    host = MagicMock()
    # bool flags
    host.isControl         = False
    host.isPlugin          = False
    host.processModeForced = False
    host.audioDriverForced = None
    host.experimental      = False
    # integer fields read by loadSettings via direct attribute access
    host.nextProcessMode      = 0
    host.processMode          = 0
    host.maxParameters        = 200
    host.uiBridgesTimeout     = 4000
    host.resetXruns           = False
    host.manageUIs            = True
    host.preferUIBridges      = True
    host.uisAlwaysOnTop       = True
    host.forceStereo          = False
    host.preferPluginBridges  = False
    host.exportLV2            = False
    host.showPluginBridges    = False
    host.showWineBridges      = False
    host.showLogs             = True
    # driver list
    host.get_engine_driver_count.return_value = 1
    host.get_engine_driver_name.return_value  = 'JACK'
    return host


@pytest.fixture
def settings_dialog(qapp):
    from carla_settings import CarlaSettingsW
    dlg = CarlaSettingsW(None, _make_host(), hasCanvas=True, hasCanvasGL=False)
    yield dlg
    dlg.close()


# ---------------------------------------------------------------------------
# Settings dialog: basic construction
# ---------------------------------------------------------------------------

def test_settings_dialog_opens(settings_dialog):
    from carla_settings import CarlaSettingsW
    assert isinstance(settings_dialog, CarlaSettingsW)


def test_settings_dialog_has_all_tabs(settings_dialog):
    from carla_settings import CarlaSettingsW
    dlg = settings_dialog
    assert dlg.ui.lw_page.rowCount() >= CarlaSettingsW.TAB_INDEX_EXPERIMENTAL + 1


# ---------------------------------------------------------------------------
# Default-project widgets (feature/default-session-on-open regression)
# ---------------------------------------------------------------------------

def test_settings_has_default_project_lineedit(settings_dialog):
    assert hasattr(settings_dialog.ui, 'le_main_default_project'), \
        'le_main_default_project widget missing from settings UI'


def test_settings_has_default_project_button(settings_dialog):
    assert hasattr(settings_dialog.ui, 'b_main_default_project_open'), \
        'b_main_default_project_open button missing from settings UI'


def test_settings_default_project_lineedit_initially_empty(settings_dialog):
    text = settings_dialog.ui.le_main_default_project.text()
    assert text == '', f'Expected empty default project path, got {text!r}'


def test_settings_default_project_lineedit_accepts_text(settings_dialog):
    dlg = settings_dialog
    dlg.ui.le_main_default_project.setText('/tmp/test.carxp')
    assert dlg.ui.le_main_default_project.text() == '/tmp/test.carxp'
    dlg.ui.le_main_default_project.setText('')


# ---------------------------------------------------------------------------
# Project-folder widget (pre-existing)
# ---------------------------------------------------------------------------

def test_settings_has_proj_folder_lineedit(settings_dialog):
    assert hasattr(settings_dialog.ui, 'le_main_proj_folder')


def test_settings_proj_folder_is_nonempty(settings_dialog):
    text = settings_dialog.ui.le_main_proj_folder.text()
    assert text, 'Expected a non-empty project folder default'


# ---------------------------------------------------------------------------
# DSP refresh spinbox (feature/dsp-bar-refresh-rate regression)
# ---------------------------------------------------------------------------

def test_settings_has_dsp_refresh_spinbox(settings_dialog):
    assert hasattr(settings_dialog.ui, 'sb_main_dsp_refresh_interval'), \
        'sb_main_dsp_refresh_interval spinbox missing — dsp-refresh feature may have been lost'


def test_settings_dsp_refresh_range(settings_dialog):
    sb = settings_dialog.ui.sb_main_dsp_refresh_interval
    assert sb.minimum() >= 1
    assert sb.maximum() >= 100


# ---------------------------------------------------------------------------
# Reset path
# ---------------------------------------------------------------------------

def test_settings_reset_clears_default_project(settings_dialog):
    from carla_settings import CarlaSettingsW
    dlg = settings_dialog
    dlg.ui.lw_page.selectRow(CarlaSettingsW.TAB_INDEX_MAIN)
    dlg.ui.le_main_default_project.setText('/tmp/something.carxp')
    dlg.slot_resetSettings()
    assert dlg.ui.le_main_default_project.text() == '', \
        'slot_resetSettings should clear le_main_default_project'


# ---------------------------------------------------------------------------
# Canvas tab visible
# ---------------------------------------------------------------------------

def test_settings_canvas_tab_visible(settings_dialog):
    from carla_settings import CarlaSettingsW
    dlg = settings_dialog
    # hasCanvas=True so row should NOT be hidden
    assert not dlg.ui.lw_page.isRowHidden(CarlaSettingsW.TAB_INDEX_CANVAS)
