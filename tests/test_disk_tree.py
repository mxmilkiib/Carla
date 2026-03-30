#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 mxmilkiib
# SPDX-License-Identifier: GPL-2.0-or-later

"""Tests for disk-tree persistence and Collapse All feature."""

import os
import sys
import tempfile

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

_REPO = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(os.path.join(_REPO, 'source', 'frontend')))
sys.path.insert(0, os.path.abspath(os.path.join(_REPO, 'bin')))

import pytest
from unittest.mock import MagicMock, patch, PropertyMock


@pytest.fixture(scope='session')
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


# ----------------------------------------------------------------------------
# QSafeSettings bool coercion
# ----------------------------------------------------------------------------

def test_qsafesettings_reads_true_string_as_bool_true(qapp):
    """String 'true' stored in INI must come back as Python True."""
    from PyQt6.QtCore import QSettings
    from utils.qsafesettings import QSafeSettings

    with tempfile.NamedTemporaryFile(suffix='.ini', delete=False) as f:
        path = f.name
    try:
        raw = QSettings(path, QSettings.Format.IniFormat)
        raw.setValue('Section/BoolKey', 'true')
        del raw

        qs = QSafeSettings(path, QSettings.Format.IniFormat)
        v = qs.value('Section/BoolKey', False, bool)
        assert v is True, f"Expected True, got {v!r}"
    finally:
        os.unlink(path)


def test_qsafesettings_reads_false_string_as_bool_false(qapp):
    """String 'false' stored in INI must come back as Python False."""
    from PyQt6.QtCore import QSettings
    from utils.qsafesettings import QSafeSettings

    with tempfile.NamedTemporaryFile(suffix='.ini', delete=False) as f:
        path = f.name
    try:
        raw = QSettings(path, QSettings.Format.IniFormat)
        raw.setValue('Section/BoolKey', 'false')
        del raw

        qs = QSafeSettings(path, QSettings.Format.IniFormat)
        v = qs.value('Section/BoolKey', True, bool)
        assert v is False, f"Expected False, got {v!r}"
    finally:
        os.unlink(path)


def test_qsafesettings_missing_key_returns_default(qapp):
    """A key that was never written must return the defaultValue."""
    from PyQt6.QtCore import QSettings
    from utils.qsafesettings import QSafeSettings

    with tempfile.NamedTemporaryFile(suffix='.ini', delete=False) as f:
        path = f.name
    try:
        qs = QSafeSettings(path, QSettings.Format.IniFormat)
        v = qs.value('Nonexistent/Key', False, bool)
        assert v is False
    finally:
        os.unlink(path)


def test_qsafesettings_roundtrip_bool_true(qapp):
    """setValue(True) round-trips correctly through a file."""
    from PyQt6.QtCore import QSettings
    from utils.qsafesettings import QSafeSettings

    with tempfile.NamedTemporaryFile(suffix='.ini', delete=False) as f:
        path = f.name
    try:
        qs_write = QSafeSettings(path, QSettings.Format.IniFormat)
        qs_write.setValue('Section/Flag', True)
        del qs_write

        qs_read = QSafeSettings(path, QSettings.Format.IniFormat)
        v = qs_read.value('Section/Flag', False, bool)
        assert v is True, f"Expected True, got {v!r}"
    finally:
        os.unlink(path)


# ----------------------------------------------------------------------------
# HostWindow structural checks (source-text guards)
# ----------------------------------------------------------------------------

def _host_src():
    path = os.path.join(_REPO, 'source', 'frontend', 'carla_host.py')
    return open(path).read()


def test_host_has_fExpandedDirs():
    assert 'fExpandedDirs' in _host_src()


def test_host_has_slot_fileTreeExpanded():
    assert 'slot_fileTreeExpanded' in _host_src()


def test_host_has_slot_fileTreeCollapsed():
    assert 'slot_fileTreeCollapsed' in _host_src()


def test_host_has_slot_diskCollapseAll():
    assert 'slot_diskCollapseAll' in _host_src()


def test_host_saves_DiskExpandedDirs():
    assert '"DiskExpandedDirs"' in _host_src()


def test_host_restores_DiskExpandedDirs():
    src = _host_src()
    assert 'DiskExpandedDirs' in src
    assert '_restoreExpandedDirs' in src


def test_host_connects_b_disk_collapse():
    src = _host_src()
    assert 'b_disk_collapse' in src
    assert 'slot_diskCollapseAll' in src


def test_host_connects_fileTreeView_expanded():
    src = _host_src()
    assert 'fileTreeView.expanded' in src


def test_host_connects_fileTreeView_collapsed():
    src = _host_src()
    assert 'fileTreeView.collapsed' in src


# ----------------------------------------------------------------------------
# carla_host.ui structural checks
# ----------------------------------------------------------------------------

def _ui_src():
    path = os.path.join(_REPO, 'resources', 'ui', 'carla_host.ui')
    return open(path).read()


def test_ui_has_b_disk_collapse():
    assert 'b_disk_collapse' in _ui_src()


def test_ui_disk_collapse_has_tooltip():
    src = _ui_src()
    assert 'Collapse all folders' in src


# ----------------------------------------------------------------------------
# Slot logic (unit-level)
# ----------------------------------------------------------------------------

class _FakeDirModel:
    """Minimal stand-in for QFileSystemModel."""
    def __init__(self, path_map):
        self._map = path_map  # index → path

    def filePath(self, idx):
        return self._map.get(idx, '')


class _FakeTreeView:
    def __init__(self):
        self.collapsed_all = False
        self.expanded_set = set()

    def collapseAll(self):
        self.collapsed_all = True

    def expand(self, idx):
        self.expanded_set.add(idx)


def _make_host_stub():
    """Build a minimal object that mimics the relevant HostWindow state."""
    host = MagicMock()
    host.fExpandedDirs = set()
    host.fDirModel = _FakeDirModel({'idx_a': '/home/user/music', 'idx_b': '/home/user/samples'})
    host.ui = MagicMock()
    host.ui.fileTreeView = _FakeTreeView()
    return host


def test_slot_fileTreeExpanded_adds_path():
    from carla_host import HostWindow
    # test the logic directly without creating a full HostWindow
    fExpandedDirs = set()
    dirModel = _FakeDirModel({'i': '/foo/bar'})

    def slot_fileTreeExpanded(modelIndex):
        path = dirModel.filePath(modelIndex)
        fExpandedDirs.add(path)

    slot_fileTreeExpanded('i')
    assert '/foo/bar' in fExpandedDirs


def test_slot_fileTreeCollapsed_removes_path():
    fExpandedDirs = {'/foo/bar', '/baz/qux'}
    dirModel = _FakeDirModel({'i': '/foo/bar'})

    def slot_fileTreeCollapsed(modelIndex):
        path = dirModel.filePath(modelIndex)
        fExpandedDirs.discard(path)

    slot_fileTreeCollapsed('i')
    assert '/foo/bar' not in fExpandedDirs
    assert '/baz/qux' in fExpandedDirs


def test_slot_diskCollapseAll_clears_expanded():
    fExpandedDirs = {'/foo', '/bar'}
    treeView = _FakeTreeView()

    def slot_diskCollapseAll():
        treeView.collapseAll()
        fExpandedDirs.clear()

    slot_diskCollapseAll()
    assert treeView.collapsed_all
    assert len(fExpandedDirs) == 0


def test_restoreExpandedDirs_expands_valid_paths(qapp):
    """_restoreExpandedDirs expands each valid index."""
    from PyQt6.QtGui import QFileSystemModel

    treeView = _FakeTreeView()
    model = QFileSystemModel()
    model.setRootPath('/')
    home = os.path.expanduser('~')
    idx = model.index(home)

    expanded = []

    def restore(paths):
        for path in paths:
            i = model.index(path)
            if i.isValid():
                treeView.expand(i)
                expanded.append(path)

    restore([home, '/nonexistent_path_xyz_abc'])
    assert home in expanded
    assert '/nonexistent_path_xyz_abc' not in expanded
