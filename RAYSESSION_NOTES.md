# RaySession Feature Survey Notes

Features reviewed from https://github.com/Houston4444/RaySession and its manual.
Listed roughly by implementation effort (ascending).

## Low-hanging fruit — implement in Carla

### Already done this session
- **Disk tree expanded-dir persistence** — RaySession remembers which folders were open in
  its file browser; now matches that in Carla.
- **Plugin sidebar** — RaySession has a "New Client" panel with searchable application list;
  Carla now has a "Plugins" sidebar tab with search + type filter.

### Practical / quick wins

1. **Patchbay group search overlay** (#carla-issue)
   - A floating search bar (`Ctrl+F` on the patchbay tab) that highlights or
     hides groups whose name doesn't match the query.
   - RaySession has this in its patchbay; Carla's patchcanvas exposes
     `findGroupByName` / `focusGroupUsingGroupName` internally.
   - Approach: `QLineEdit` above `graphicsView`, connected to a filter that
     calls `patchcanvas.setGroupVisible(groupId, bool)` per group.

2. **Xrun counter auto-reset on project load**
   - RaySession resets xrun counters on session load.
   - Carla has a per-engine xrun counter (`b_xruns` button) but doesn't
     reset it automatically when a project is loaded.
   - One-liner in `slot_handleProjectLoadFinishedCallback`.

3. **Canvas screenshot shortcut improvement**
   - RaySession has a dedicated "Export patchbay as PNG/SVG" button.
   - Carla has `act_canvas_save_image` but it's buried in the menu.
   - Add a toolbar button or keyboard shortcut.

4. **Session notes / metadata**
   - RaySession lets one attach a text note to a session.
   - Could be a simple `.carla-notes.txt` stored alongside the project file
     and shown in a dock widget.

5. **Recent sessions list improvements**
   - RaySession shows session thumbnails and dates in an "Open Recent" dialog.
   - Carla's `menu_Open_Recent` is already there; could show last-modified
     dates and allow pinning.

6. **Default BPM / sample rate saved per project**
   - RaySession stores `jack_config` with BPM/SR per session.
   - Carla already saves `LastBPM` to QSettings globally; per-project would
     be more useful.

## Medium effort

7. **Patchbay group fold / wrap** — collapse a group to show only its label,
   hiding all port rows. patchcanvas would need a `foldGroup(groupId)` API.

8. **JACK patchbay external connections saved to project** — save the
   connections visible in patchbay (external clients) as part of the `.carxp`
   file so they're restored on load. RaySession's `ray-jackpatch` does this.

9. **Session templates** — "Save as Template" archives the current `.carxp`
   (plugins + connections) as a re-usable starting point accessible from File >
   New from Template.

## Out of scope for Carla (session-manager concerns)

- Git-based snapshots (requires git subprocess; better done by the session
  manager layer)
- Network sub-sessions
- Virtual desktop assignment
- `ray_control` CLI (Carla has its own OSC interface)
