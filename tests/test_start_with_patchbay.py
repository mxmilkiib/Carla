#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 mxmilkiib
# SPDX-License-Identifier: GPL-2.0-or-later

"""Tests for the start-with-patchbay setting and viewport centering on load."""

import os
import sys

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

_REPO = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(os.path.join(_REPO, 'source', 'frontend')))
sys.path.insert(0, os.path.abspath(os.path.join(_REPO, 'bin')))

import pytest
from unittest.mock import MagicMock


@pytest.fixture(scope='session')
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def settings_dialog(qapp):
    from carla_settings import CarlaSettingsW
    host = MagicMock()
    host.isControl = False
    host.isPlugin = False
    host.audioDriverForced = None
    host.processModeForced = False
    host.uisAlwaysOnTop = False
    host.showLogs = False
    host.experimental = False
    dlg = CarlaSettingsW(None, host, True, False)
    yield dlg
    dlg.close()


def test_settings_has_start_patchbay_checkbox(settings_dialog):
    from PyQt6.QtWidgets import QCheckBox
    dlg = settings_dialog
    assert hasattr(dlg.ui, 'ch_main_start_patchbay')
    assert isinstance(dlg.ui.ch_main_start_patchbay, QCheckBox)


def test_start_patchbay_default_is_false():
    from carla_shared import CARLA_DEFAULT_MAIN_START_WITH_PATCHBAY
    assert CARLA_DEFAULT_MAIN_START_WITH_PATCHBAY is False


def test_settings_reset_clears_start_patchbay(settings_dialog):
    from carla_settings import CarlaSettingsW
    dlg = settings_dialog
    dlg.ui.ch_main_start_patchbay.setChecked(True)
    dlg.ui.lw_page.selectRow(CarlaSettingsW.TAB_INDEX_MAIN)
    dlg.slot_resetSettings()
    assert not dlg.ui.ch_main_start_patchbay.isChecked()


def test_zoom_fit_scheduled_after_project_load():
    src = open(os.path.join(_REPO, 'source', 'frontend', 'carla_host.py')).read()
    assert 'slot_canvasZoomFit' in src
    assert 'projectLoadingFinished' in src
