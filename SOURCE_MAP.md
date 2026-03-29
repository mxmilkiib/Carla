# Carla Source Map

Quick reference for navigating the Carla codebase.
Generated 2026-03-30. Repo root: `/home/milkii/media/projects/cascade/carla`.

---

## Top-level layout

```
carla/
├── source/          C++ backend + Python frontend + modules
├── resources/       Qt .ui files, icons, themes, .qrc
├── data/            Desktop entries, LADSPA/LV2/VST meta, man pages
├── doc/             Doxygen config, api.h stub
├── bin/             Build output (gitignored): .so, .py symlinks, resources/
├── tests/           Local pytest suite (test_frontend.py, test_settings_dialog.py)
├── cmake/           CMake find-modules (FindXxx.cmake)
├── Makefile         Top-level build (includes source/Makefile.mk)
├── Makefile.dist.mk install/uninstall targets
├── meson.build      Alternative Meson build
└── INTEGRATION.md   Local branch/integration tracking doc
```

---

## `source/` subsystems

### `source/backend/` — C++ plugin/engine core

| File / dir | Role |
|---|---|
| `CarlaBackend.h` | Public enums + structs: `PluginType`, `EngineProcessMode`, `ParameterData`, `ParameterRanges`, … |
| `CarlaEngine.hpp` | `CarlaEngine` base class: plugin management, transport, OSC, callbacks |
| `CarlaPlugin.hpp` | `CarlaPlugin` base class: parameter/port/program/MIDI API |
| `CarlaHost.h` | Flat C API (`carla_*()`) wrapping the engine — used by the Python `ctypes` bindings |
| `CarlaUtils.h` | Utility C API: discovery, file utilities, `carla_get_*()` helpers |
| `CarlaStandalone.cpp` | Implements `CarlaHost.h` for the standalone `.so` (`libcarla_standalone2`) |
| `CarlaStandaloneNSM.cpp` | NSM session manager integration |

#### `source/backend/engine/`

| File | Role |
|---|---|
| `CarlaEngine.cpp` | Engine base: plugin add/remove, transport, callbacks, OSC dispatch |
| `CarlaEngineBridge.cpp` | Child-process bridge engine (plugin ↔ host IPC via pipes/shared memory) |
| `CarlaEngineJack.cpp` | JACK audio/MIDI engine driver |
| `CarlaEngineNative.cpp` | Native plugin wrapping engine — exposes all loaded plugins as one `NativePlugin`; also the UI server that feeds the Python frontend over a pipe |
| `CarlaEngineGraph.cpp` | Patchbay graph: port groups, connections, `CarlaEngineGraph` |
| `CarlaEngineOsc.cpp/Send/Handlers` | OSC server (UDP) for remote control |
| `CarlaEngineRtAudio.cpp` | RtAudio driver (ALSA, PulseAudio, CoreAudio, …) |
| `CarlaEngineSDL.cpp` | SDL2 audio driver |
| `CarlaEnginePorts.cpp` | `CarlaEngineAudioPort`, `CarlaEngineCVPort`, `CarlaEngineMidiPort` |
| `CarlaEngineRunner.cpp` | Real-time runner thread |
| `CarlaEngineInternal.hpp/.cpp` | Internal engine state, plugin list, mutex helpers |

#### `source/backend/plugin/`

| File | Role |
|---|---|
| `CarlaPlugin.cpp` | Base plugin implementation (params, programs, custom data, state save/load) |
| `CarlaPluginBridge.cpp` | Out-of-process bridge client: communicates with `CarlaBridgePlugin` via shared memory + pipes |
| `CarlaPluginLV2.cpp` | LV2 plugin (largest file, ~318 KB): ports, URIs, worker, state, UI, MIDI |
| `CarlaPluginVST2.cpp` | VST2 via FST/hvst wrappers |
| `CarlaPluginVST3.cpp` | VST3 via Steinberg SDK |
| `CarlaPluginCLAP.cpp` | CLAP plugin |
| `CarlaPluginNative.cpp` | Built-in native plugins (wraps `NativePlugin` interface) |
| `CarlaPluginLADSPADSSI.cpp` | LADSPA + DSSI |
| `CarlaPluginFluidSynth.cpp` | FluidSynth SF2/SF3 player |
| `CarlaPluginJSFX.cpp` | REAPER JSFX via ysfx library |
| `CarlaPluginJack.cpp` | JACK application as plugin |
| `CarlaPluginAU.cpp` | Audio Units (macOS) |
| `CarlaPluginSFZero.cpp` | SFZ via SFZero |

#### `source/backend/utils/`

Discovery, file scanning, LADSPA-RDF loader, LV2 world loader.

---

### `source/bridges-plugin/` — out-of-process bridge host

`CarlaBridgePlugin.cpp` — loads a plugin (LV2, VST2, …) in a child process and communicates back to `CarlaPluginBridge` in the main process via shared memory + `CarlaPipeServer`. One executable per plugin type (e.g. `carla-bridge-lv2-x86_64`).

### `source/bridges-ui/` — out-of-process UI bridge

Runs a plugin's native UI in a separate process. `CarlaBridgeUI.cpp` + per-toolkit wrappers (`CarlaBridgeToolkitGtk2/3.cpp`, `…Qt4/5.cpp`, `…X11.cpp`).

### `source/discovery/` — plugin scanner

`CarlaPluginDiscovery.cpp` — scanned by `carla-discovery-*` binaries; outputs plugin metadata to stdout for the plugin cache.

### `source/plugin/` — Carla as a plugin

| File | Role |
|---|---|
| `carla-lv2.cpp` | Carla exported as an LV2 plugin (`carla.lv2`) |
| `carla-lv2-export.cpp` | LV2 manifest/RDF generation |
| `carla-vst.cpp` | Carla exported as a VST2 plugin |
| `carla-native-plugin.cpp` | Carla exported as a native plugin (for use inside Carla itself) |
| `carla-host-plugin.cpp` | Shared host-plugin glue |

### `source/libjack/` — JACK replacement library

`libjack.so` shim that intercepts JACK API calls from applications and routes them into the Carla engine (for the "JACK application as plugin" feature).

### `source/interposer/` — LD_PRELOAD helpers

X11 and audio interposers for sandboxing bridge UIs.

### `source/rest/` — REST API

HTTP/WebSocket frontend (`carla-host.cpp`) wrapping `CarlaHost.h`; used by the web UI (`carla_backend_qtweb.py`).

### `source/native-plugins/` — built-in native plugins

`audio-file.cpp`, `midi-pattern.cpp`, `xycontroller.cpp`, `bigmeter.cpp`, MIDI tools, etc. Compiled into the backend.

### `source/theme/` — Qt style

`CarlaStyle.cpp/hpp` — custom QStyle for the dark Pro Theme.

### `source/includes/` — shared headers

`CarlaNative.h` (native plugin ABI), `CarlaDefines.h`, `CarlaMutex.hpp`, `CarlaRingBuffer.hpp`, `CarlaString.hpp`, `CarlaPipeUtils.hpp`, OS/compiler detection macros, LADSPA/LV2/VST SDK re-exports.

### `source/jackbridge/` — JACK runtime bridge

`JackBridge.cpp` — dynamically loads `libjack.so` at runtime so Carla can build without JACK being present at compile time.

### `source/modules/` — vendored third-party libraries

DISTRHO Plugin Framework (DPF), FluidSynth, lilv/serd/sord/sratom (LV2 world), rtaudio, rtmidi, sfizz, ysfx, zita-resampler, and more. Each is a self-contained subdirectory.

---

## `source/frontend/` — Python Qt UI

### Entry-point executables (shebang scripts)

| Script | What it launches |
|---|---|
| `carla` | Rack view (`CarlaApplication` + `CarlaHostWindow`) |
| `carla-patchbay` | Patchbay view |
| `carla-rack` | Rack view (alias) |
| `carla-plugin` | Embedded plugin UI (used by `carla-lv2`/`carla-vst`) |
| `carla-plugin-patchbay` | Embedded plugin UI, patchbay layout |
| `carla-control` | Remote OSC control surface |
| `carla-jack-single/multi` | JACK app wrappers |
| `carla-rest-frontend` | REST/web UI launcher |

### Core Python modules

| File | Role |
|---|---|
| `carla_shared.py` | Constants (`CARLA_KEY_*`, `CARLA_DEFAULT_*`), OS detection, `HOST` setup, shared helpers |
| `carla_backend.py` | `ctypes` bindings for `libcarla_standalone2.so` — maps every `carla_*()` C function |
| `carla_backend_qt.py` | `CarlaHostQtNull` / `CarlaHostQtPlugin` — Qt-aware host shims |
| `carla_host.py` | `CarlaHostW` — main window; plugin rack/patchbay, transport bar, DSP meter, menus, engine start/stop, project load/save, settings integration |
| `carla_settings.py` | `CarlaSettingsW` (QDialog) — all settings tabs: Main, Canvas, Engine, OSC, File Paths, Plugin Paths, Wine, Experimental |
| `carla_skin.py` | Plugin slot skins (`CarlaPluginW` subclasses): Default, Classic, Compact, Calf, Presets |
| `carla_widgets.py` | `CarlaAboutW`, `CarlaEditW`, plugin parameter widgets, MIDI program list |
| `carla_app.py` | `CarlaApplication` subclass of `QApplication`: theme/palette setup, signal handling |
| `carla_utils.py` | `ctypes` bindings for `libcarla_utils.so` (discovery, file utils) |
| `qt_compat.py` | Qt5/Qt6 compatibility shim: re-exports enum aliases so code uses `Qt.AlignLeft` regardless of version |
| `qt_config.py` | Generated: `qt = 5` or `qt = 6` — single source of truth for which Qt version the frontend uses |
| `externalui.py` | `ExternalUI` base for out-of-process UI scripts (bigmeter, xycontroller, …) |
| `ladspa_rdf.py` | Pure-Python LADSPA-RDF reader |

### Generated UI bindings (`ui_*.py`)

PyUIC-generated from `resources/ui/*.ui`. Regenerate with `make generate-ui`. Version must match `qt_config.py`.

### `patchcanvas/` — signal-flow patchbay canvas

| File | Role |
|---|---|
| `__init__.py` | Public API: `init()`, `addGroup()`, `addPort()`, `connectPorts()`, `setGroupPos()`, … |
| `patchcanvas.py` | Core state machine: group/port registries, animation manager, scene rect management |
| `scene.py` | `PatchScene(QGraphicsScene)`: rubber-band select, drag-scroll, zoom, context menus |
| `canvasbox.py` | `CanvasBox(QGraphicsItem)`: plugin group box, port layout |
| `canvasport.py` | `CanvasPort(QGraphicsItem)`: individual port, hover/select |
| `canvasportgroup.py` | `CanvasPortGroup`: stereo/multi-channel port pairs |
| `canvasline.py` / `canvasbezierline.py` | Connection lines (straight and bezier) |
| `canvaslinemov.py` / `canvasbezierlinemov.py` | In-progress connection drag lines |
| `theme.py` | `Theme` dataclass: colours, pen widths, font sizes per theme variant |
| `utils.py` | `CanvasItemFX`, z-ordering, `getPluginIcon()` |

### `widgets/` — reusable Qt widgets (Python + optional C++ twins)

`CommondDial`, `PixmapDial`, `ScalableDial`, `ParamSpinBox`, `DigitalPeakMeter`, `PixmapKeyboard`, `PianoRoll`, `LedButton`, `CanvasPreviewFrame`, `DraggableGraphicsView`, `RackListWidget`, `ScalableButton`, `CollapsableWidget`.

Many have a `.py` pure-Python version and a `.cpp` C++ version compiled into `libcarla_frontend.so` for performance.

### `dialogs/` and `pluginlist/`

Subdialogs: plugin browser (`pluginlist/`), MIDI keyboard dialog, JACK patchbay port dialog, add-plugin wizard.

---

## `resources/` — assets

```
resources/
├── ui/          Qt Designer .ui files (→ source/frontend/ui_*.py via pyuic)
├── icons/       SVG/SVGZ icons (Breeze + custom)
├── themes/      QSS stylesheets for CarlaStyle
├── patchcanvas/ Canvas theme images
└── resources.qrc  Qt resource manifest (→ resources_rc.py via pyrcc)
```

---

## Build system

| File | Role |
|---|---|
| `Makefile` | Top-level: orchestrates `source/`, `resources/`, install; custom targets: `generate-ui`, `check`, `test` |
| `source/Makefile.mk` | Recursively builds all `source/` subdirs in dependency order |
| `source/Makefile.deps.mk` | Qt/PyQt detection; sets `FRONTEND_TYPE`, `PYUIC`, `PYRCC`, `HAVE_*` flags |
| `Makefile.dist.mk` | `install` / `uninstall` / packaging |
| `meson.build` | Alternative Meson build (partial feature parity) |

Build output lands in `bin/`. Generated Python files (`qt_config.py`, `ui_*.py`, `resources_rc.py`) are gitignored.

---

## Data flow: plugin parameter lifecycle

```
Plugin (LV2/VST2/…)
  │  getParameterScalePointCount/Value/Label
  │
CarlaPlugin{LV2,VST2,…}  [source/backend/plugin/]
  │  getParameter{Data,Ranges,Value}
  │
CarlaEngine  [source/backend/engine/CarlaEngine.cpp]
  │  ── OSC: PARAMETER_DATA / PARAMETER_SCALEPOINT_  ──►  carla_host.py (Python frontend)
  │  ── NativePlugin pipe (CarlaEngineNative.cpp)   ──►  carla-lv2 / carla-vst plugin UI
  │
CarlaHostW.slot_handleParameterValueChangedCallback
  │
CarlaPluginW (carla_skin.py)  ──►  ParamSpinBox / PixmapDial widgets
```

---

## Tests

```
tests/
├── test_frontend.py       13 source-scan tests: key/default consistency,
│                          fSavedSettings coverage, feature-branch regressions,
│                          patchcanvas + widget import smoke tests
└── test_settings_dialog.py  12 offscreen UI tests: CarlaSettingsW construction,
                             widget existence, reset path, DSP refresh spinbox
```

Run with `make test` (sets `QT_QPA_PLATFORM=offscreen`).
