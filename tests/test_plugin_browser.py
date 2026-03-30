#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 mxmilkiib
# SPDX-License-Identifier: GPL-2.0-or-later

"""Tests for the PluginBrowserWidget sidebar panel."""

import json
import os
import sys

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

_REPO = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(os.path.join(_REPO, 'source', 'frontend')))
sys.path.insert(0, os.path.abspath(os.path.join(_REPO, 'bin')))

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(scope='session')
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def browser(qapp):
    from carla_plugin_browser import PluginBrowserWidget
    w = PluginBrowserWidget()
    yield w
    w.close()


# ----------------------------------------------------------------------------
# Construction
# ----------------------------------------------------------------------------

def test_browser_widget_creates(browser):
    from carla_plugin_browser import PluginBrowserWidget
    from PyQt6.QtWidgets import QWidget
    assert isinstance(browser, QWidget)


def test_browser_has_search_line_edit(browser):
    from PyQt6.QtWidgets import QLineEdit
    assert hasattr(browser, '_search')
    assert isinstance(browser._search, QLineEdit)


def test_browser_has_filter_combo(browser):
    from PyQt6.QtWidgets import QComboBox
    assert hasattr(browser, '_filterCombo')
    assert isinstance(browser._filterCombo, QComboBox)


def test_browser_has_list_widget(browser):
    from PyQt6.QtWidgets import QListWidget
    assert hasattr(browser, '_list')
    assert isinstance(browser._list, QListWidget)


def test_browser_filter_combo_has_all_types(browser):
    combo = browser._filterCombo
    assert combo.count() >= 3
    texts = [combo.itemText(i) for i in range(combo.count())]
    assert 'All types' in texts
    assert 'Internal' in texts
    assert 'LV2' in texts


# ----------------------------------------------------------------------------
# Initial state
# ----------------------------------------------------------------------------

def test_browser_starts_empty(browser):
    assert browser._list.count() == 0
    assert not browser._loaded


# ----------------------------------------------------------------------------
# refresh() when utils not available
# ----------------------------------------------------------------------------

def test_refresh_without_utils_shows_message(browser, qapp):
    from carla_plugin_browser import PluginBrowserWidget
    import carla_plugin_browser as mod
    original = getattr(mod.gCarla, 'utils', None)
    try:
        mod.gCarla.utils = None
        browser.refresh()
        assert browser._list.count() == 0
        assert 'not loaded' in browser._status.text().lower() or \
               'engine' in browser._status.text().lower()
    finally:
        mod.gCarla.utils = original


# ----------------------------------------------------------------------------
# refresh() with mocked utils
# ----------------------------------------------------------------------------

def _make_mock_utils(internal_plugins, lv2_plugins):
    """Return a mock gCarla.utils that serves the given plugin lists."""
    from carla_backend import PLUGIN_INTERNAL, PLUGIN_LV2

    def _count(ptype, path):
        if ptype == PLUGIN_INTERNAL:
            return len(internal_plugins)
        if ptype == PLUGIN_LV2:
            return len(lv2_plugins)
        return 0

    def _info(ptype, index):
        if ptype == PLUGIN_INTERNAL:
            return internal_plugins[index]
        if ptype == PLUGIN_LV2:
            return lv2_plugins[index]
        return {'valid': False, 'name': '', 'label': '', 'maker': ''}

    utils = MagicMock()
    utils.get_cached_plugin_count.side_effect = _count
    utils.get_cached_plugin_info.side_effect = _info
    return utils


def test_refresh_loads_internal_plugins(browser, qapp):
    import carla_plugin_browser as mod
    from carla_backend import PLUGIN_INTERNAL, BINARY_NATIVE

    fakes = [
        {'valid': True, 'name': 'ZynAddSubFX', 'label': 'ZynAddSubFX', 'maker': 'zynaddsubfx'},
        {'valid': True, 'name': 'MIDI to CV',  'label': 'midiCV',       'maker': 'carla'},
    ]
    original = mod.gCarla.utils
    try:
        mod.gCarla.utils = _make_mock_utils(fakes, [])
        browser.refresh()
        assert browser._loaded
        assert browser._list.count() == 2
        assert browser._plugins[0]['ptype'] == PLUGIN_INTERNAL
        assert browser._plugins[0]['btype'] == BINARY_NATIVE
    finally:
        mod.gCarla.utils = original


def test_refresh_skips_invalid_plugins(browser, qapp):
    import carla_plugin_browser as mod

    fakes = [
        {'valid': False, 'name': 'Bad',  'label': 'bad',  'maker': ''},
        {'valid': True,  'name': 'Good', 'label': 'good', 'maker': 'x'},
    ]
    original = mod.gCarla.utils
    try:
        mod.gCarla.utils = _make_mock_utils(fakes, [])
        browser.refresh()
        assert browser._list.count() == 1
        assert browser._list.item(0).text() == '[Int] Good'
    finally:
        mod.gCarla.utils = original


def test_refresh_loads_lv2_plugins(browser, qapp):
    import carla_plugin_browser as mod
    from carla_backend import PLUGIN_LV2

    lv2s = [
        {'valid': True, 'name': 'Calf Compressor', 'label': 'http://calf.sourceforge.net/plugins/Compressor', 'maker': 'Calf'},
    ]
    original = mod.gCarla.utils
    try:
        mod.gCarla.utils = _make_mock_utils([], lv2s)
        browser.refresh()
        assert any(p['ptype'] == PLUGIN_LV2 for p in browser._plugins)
        lv2_item = next(
            browser._list.item(i)
            for i in range(browser._list.count())
            if browser._list.item(i).text().startswith('[LV2]')
        )
        assert 'Calf Compressor' in lv2_item.text()
    finally:
        mod.gCarla.utils = original


# ----------------------------------------------------------------------------
# Search filter
# ----------------------------------------------------------------------------

def test_search_filter_hides_non_matching(browser, qapp):
    import carla_plugin_browser as mod

    fakes = [
        {'valid': True, 'name': 'ZynAddSubFX', 'label': 'ZynAddSubFX', 'maker': 'zyn'},
        {'valid': True, 'name': 'MIDI to CV',  'label': 'midiCV',       'maker': 'carla'},
    ]
    original = mod.gCarla.utils
    try:
        mod.gCarla.utils = _make_mock_utils(fakes, [])
        browser.refresh()
        browser._search.setText('zyn')
        assert browser._list.count() == 1
        assert 'ZynAddSubFX' in browser._list.item(0).text()
    finally:
        mod.gCarla.utils = original
        browser._search.clear()


def test_search_clear_restores_all(browser, qapp):
    import carla_plugin_browser as mod

    fakes = [
        {'valid': True, 'name': 'Alpha', 'label': 'alpha', 'maker': 'a'},
        {'valid': True, 'name': 'Beta',  'label': 'beta',  'maker': 'b'},
    ]
    original = mod.gCarla.utils
    try:
        mod.gCarla.utils = _make_mock_utils(fakes, [])
        browser.refresh()
        browser._search.setText('alpha')
        assert browser._list.count() == 1
        browser._search.clear()
        assert browser._list.count() == 2
    finally:
        mod.gCarla.utils = original


# ----------------------------------------------------------------------------
# pluginActivated signal
# ----------------------------------------------------------------------------

def test_double_click_emits_signal(browser, qapp):
    import carla_plugin_browser as mod

    fakes = [{'valid': True, 'name': 'TestPlug', 'label': 'testplug', 'maker': 'tester'}]
    original = mod.gCarla.utils
    received = []
    browser.pluginActivated.connect(received.append)
    try:
        mod.gCarla.utils = _make_mock_utils(fakes, [])
        browser.refresh()
        item = browser._list.item(0)
        browser._list.itemDoubleClicked.emit(item)
        assert len(received) == 1
        assert received[0]['name'] == 'TestPlug'
        assert received[0]['label'] == 'testplug'
    finally:
        mod.gCarla.utils = original
        browser.pluginActivated.disconnect(received.append)


# ----------------------------------------------------------------------------
# MIME drag data
# ----------------------------------------------------------------------------

def test_mime_type_constant():
    from carla_plugin_browser import MIME_PLUGIN_INFO
    assert isinstance(MIME_PLUGIN_INFO, str)
    assert 'carla' in MIME_PLUGIN_INFO


def test_plugin_dict_is_json_serialisable(browser, qapp):
    import carla_plugin_browser as mod

    fakes = [{'valid': True, 'name': 'Plug', 'label': 'plug', 'maker': 'dev'}]
    original = mod.gCarla.utils
    try:
        mod.gCarla.utils = _make_mock_utils(fakes, [])
        browser.refresh()
        plugin = browser._plugins[0]
        encoded = json.dumps(plugin)
        decoded = json.loads(encoded)
        assert decoded['name'] == 'Plug'
        assert decoded['label'] == 'plug'
    finally:
        mod.gCarla.utils = original


# ----------------------------------------------------------------------------
# carla_host.py structural checks (source-text regression guards)
# ----------------------------------------------------------------------------

def _host_src():
    path = os.path.join(_REPO, 'source', 'frontend', 'carla_host.py')
    return open(path).read()


def test_host_imports_plugin_browser():
    src = _host_src()
    assert 'from carla_plugin_browser import' in src


def test_host_has_slot_add_plugin_from_browser():
    src = _host_src()
    assert 'slot_addPluginFromBrowser' in src


def test_host_has_event_filter_for_drop():
    src = _host_src()
    assert 'def eventFilter' in src
    assert 'MIME_PLUGIN_INFO' in src


def test_host_applies_pending_drop_pos():
    src = _host_src()
    assert 'fPendingPluginDropPos' in src
    assert 'patchcanvas.setGroupPos' in src
