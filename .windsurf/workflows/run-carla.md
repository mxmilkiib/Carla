---
description: run carla frontend from source tree
---

Ensure the build is up to date first:

// turbo
1. Run `make -C /home/milkii/media/projects/cascade/carla -j$(nproc --ignore=2)`

Regenerate UI files if the Qt version changed or any .ui file was edited:

// turbo
2. Run `make -C /home/milkii/media/projects/cascade/carla generate-ui`

Run syntax + UI import check:

// turbo
3. Run `make -C /home/milkii/media/projects/cascade/carla check`

Launch the patchbay frontend (exits immediately without a display — check for Python tracebacks):

// turbo
4. Run `cd /home/milkii/media/projects/cascade/carla && PYTHONPATH=source/frontend:bin python3 source/frontend/carla-plugin-patchbay 2>&1 | head -30`

Launch the rack frontend:

// turbo
5. Run `cd /home/milkii/media/projects/cascade/carla && PYTHONPATH=source/frontend:bin python3 source/frontend/carla 2>&1 | head -30`
