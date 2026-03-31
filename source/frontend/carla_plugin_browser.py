#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 mxmilkiib
# SPDX-License-Identifier: GPL-2.0-or-later

"""Plugins sidebar panel for the Carla host window.

Enumerates PLUGIN_INTERNAL and PLUGIN_LV2 plugins via gCarla.utils,
displays them in a searchable, filterable list, and emits
pluginActivated(dict) when a plugin is activated by double-click.
Drag-and-drop is supported via MIME type MIME_PLUGIN_INFO.
"""

import json
import os

from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import QMimeData

from carla_backend import (
    BINARY_NATIVE,
    PLUGIN_INTERNAL,
    PLUGIN_LV2,
)
from carla_shared import (
    CARLA_KEY_PATHS_LV2,
    CARLA_DEFAULT_LV2_PATH,
    gCarla,
)
from utils.qsafesettings import QSafeSettings

# MIME type used to carry plugin info between the list and the patchbay view.
MIME_PLUGIN_INFO = 'application/x-carla-plugin-info'

_TYPE_TAG = {
    PLUGIN_INTERNAL: 'Int',
    PLUGIN_LV2: 'LV2',
}

# --------------------------------------------------------------------------------------------------------------------
# Draggable list widget


class _PluginListWidget(QListWidget):
    """QListWidget that initiates a drag carrying MIME_PLUGIN_INFO data."""

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return super().mouseMoveEvent(event)
        item = self.currentItem()
        if item is None:
            return super().mouseMoveEvent(event)
        plugin = item.data(Qt.ItemDataRole.UserRole)
        if plugin is None:
            return super().mouseMoveEvent(event)
        mime = QMimeData()
        mime.setData(MIME_PLUGIN_INFO, json.dumps(plugin).encode('utf-8'))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.CopyAction)


# --------------------------------------------------------------------------------------------------------------------
# Public widget


class PluginBrowserWidget(QWidget):
    """Sidebar panel listing installed plugins with search and type filter.

    Signals
    -------
    pluginActivated(dict)
        Emitted when the user double-clicks a plugin. The dict has keys:
        btype, ptype, filename, name, label, uniqueId, maker.
    """

    pluginActivated = pyqtSignal(dict)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._plugins = []
        self._loaded = False
        self._buildUi()

    # ----------------------------------------------------------------------------------------------------------------
    # Construction

    def _buildUi(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search plugins...")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._applyFilter)
        layout.addWidget(self._search)

        self._filterCombo = QComboBox()
        self._filterCombo.addItem("All types", None)
        self._filterCombo.addItem("Internal", PLUGIN_INTERNAL)
        self._filterCombo.addItem("LV2", PLUGIN_LV2)
        self._filterCombo.currentIndexChanged.connect(self._applyFilter)
        layout.addWidget(self._filterCombo)

        self._list = _PluginListWidget()
        self._list.setUniformItemSizes(True)
        self._list.setSortingEnabled(True)
        self._list.itemDoubleClicked.connect(self._onDoubleClick)
        layout.addWidget(self._list, stretch=1)

        hbox = QHBoxLayout()
        self._status = QLabel("Waiting for engine...")
        self._status.setStyleSheet("color: gray; font-size: 10px;")
        self._refreshBtn = QPushButton("Refresh")
        self._refreshBtn.setMaximumWidth(70)
        self._refreshBtn.clicked.connect(self.refresh)
        hbox.addWidget(self._status, stretch=1)
        hbox.addWidget(self._refreshBtn)
        layout.addLayout(hbox)

    # ----------------------------------------------------------------------------------------------------------------
    # Public API

    def refresh(self):
        """Load or reload the plugin list from gCarla.utils.

        Enumerates PLUGIN_INTERNAL (no path needed) and PLUGIN_LV2 (using
        the path saved in QSafeSettings).  Call this once the engine is
        running and gCarla.utils is available.
        """
        if gCarla.utils is None:
            self._status.setText("Engine not loaded — start the engine first")
            return

        self._plugins.clear()

        # PLUGIN_INTERNAL — always at path ""
        count = gCarla.utils.get_cached_plugin_count(PLUGIN_INTERNAL, "")
        for i in range(count):
            info = gCarla.utils.get_cached_plugin_info(PLUGIN_INTERNAL, i)
            if not info.get('valid', False):
                continue
            self._plugins.append({
                'btype':    BINARY_NATIVE,
                'ptype':    PLUGIN_INTERNAL,
                'filename': "",
                'name':     info.get('name', "") or "",
                'label':    info.get('label', "") or "",
                'uniqueId': 0,
                'maker':    info.get('maker', "") or "",
            })

        # PLUGIN_LV2 — path from settings
        settings = QSafeSettings()
        lv2PathList = settings.value(CARLA_KEY_PATHS_LV2, CARLA_DEFAULT_LV2_PATH, list)
        lv2Path = os.pathsep.join(lv2PathList) if isinstance(lv2PathList, list) \
            else (lv2PathList or "")
        count = gCarla.utils.get_cached_plugin_count(PLUGIN_LV2, lv2Path)
        for i in range(count):
            info = gCarla.utils.get_cached_plugin_info(PLUGIN_LV2, i)
            if not info.get('valid', False):
                continue
            self._plugins.append({
                'btype':    BINARY_NATIVE,
                'ptype':    PLUGIN_LV2,
                'filename': "",
                'name':     info.get('name', "") or "",
                'label':    info.get('label', "") or "",  # LV2 URI
                'uniqueId': 0,
                'maker':    info.get('maker', "") or "",
            })

        self._loaded = True
        self._populateList()

    # ----------------------------------------------------------------------------------------------------------------
    # Internal helpers

    def _populateList(self):
        filterType = self._filterCombo.currentData()
        searchText = self._search.text().lower()

        self._list.clear()
        visible = 0
        for plugin in self._plugins:
            if filterType is not None and plugin['ptype'] != filterType:
                continue
            name = plugin['name'].lower()
            maker = plugin['maker'].lower()
            if searchText and searchText not in name and searchText not in maker:
                continue
            tag = _TYPE_TAG.get(plugin['ptype'], '?')
            item = QListWidgetItem(f"[{tag}] {plugin['name']}")
            item.setData(Qt.ItemDataRole.UserRole, plugin)
            item.setToolTip(f"{plugin['maker']}\n{plugin['label']}")
            self._list.addItem(item)
            visible += 1

        total = len(self._plugins)
        self._status.setText(f"{visible} / {total} plugins")

    def _applyFilter(self):
        if self._loaded:
            self._populateList()

    def _onDoubleClick(self, item):
        plugin = item.data(Qt.ItemDataRole.UserRole)
        if plugin is not None:
            self.pluginActivated.emit(plugin)
