# Carla Integration Branch Configuration

Last updated: 2026-03-27 21:25
URL: https://gist.github.com/mxmilkiib/9c883e2022e978d9098311cbe4e2f875
[RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119)

## Overview / rules

- Purpose: This document tracks Milkii's personal Carla development setup, for creating and testing feature and bugfix branches.
- Living document: This is a living document and SHOULD be updated as the workflow evolves.
- Single repo: The goal is to maintain one Carla source instance at `/home/milkii/media/projects/cascade/carla` with both an `integrated` branch and individual feature/fix branches.
- Main sync: The `main` branch MUST maintain sync with `falktx/Carla` main. `origin/main` MUST be kept as a fast-forward mirror of `upstream/main` — run `git push --no-verify origin main` after every `git fetch upstream && git merge upstream/main` on main.
- Main read-only: The `main` branch MUST NOT receive any local commits — not `INTEGRATION.md` updates, not patches, nothing. All commits go on `integrated` or a feature/fix branch. Any stray commits on `main` MUST be removed by force-pushing the clean `upstream/main` tip.
- Integration branch: The repo MUST have an `integrated` branch that combines multiple upstream PR branches and local feature/fix branches.
- Individual branches: Each feature/fix MUST have its own branch, kept clean for upstream PRs. Branch out from `upstream/main`, never from local `main`.
- Dev location: All individual branch development is done in the same repo — checkout the branch, work, push, switch back to `integrated` for builds.
- Integration edits: `integrated` can have some edits for testing purposes, but should be kept minimal.
- Clean commits: A branch MUST have clean commits before first being linked with a GitHub PR.
- Stability: The `integrated` branch SHOULD provide a stable bleeding-edge build combining desired upstream PRs and local improvements.
- "Updating" the system: When asked to "update" or told the system has been updated, this MUST include all post-update checks in order:
  1. Fetch upstream and check for new commits on `upstream/main`
  2. Check all `[x]` branches: verify whether commits are already present in `upstream/main` (`git log upstream/main --oneline | grep <keyword>`); if fully merged, move the entry to "Merged to Upstream", remove the `[x]` marker, and record the merge date — do this BEFORE rebasing or rebuilding
  3. Rebase all non-merged feature branches on new `upstream/main` (stash any WIP first); skip branches identified as merged in step 2
  4. Rebuild the `integrated` branch: merge `upstream/main` then re-merge all `[x]` branches in order, resolving any conflicts
  5. Build the `integrated` branch (`make -j$(nproc --ignore=2)`) and verify it succeeds
  6. Check all open PRs for new review feedback and update `INTEGRATION.md` statuses accordingly
  7. Update the "Last updated" timestamp and rebuild log entry in `INTEGRATION.md`, commit, and sync to Gist
- Merge process: The integration merge process MUST follow the steps in the Integration Merge Process section below.
- Rebase hygiene: All branches SHOULD be kept up-to-date and rebased with `falktx/Carla` main to minimise merge conflicts, except merged branches.
- Rebase first: A branch MUST be rebased as an initial step before any new change is made to said branch.
- Incremental PRs: Changes to `falktx/Carla` PRs MUST be incremental so as to be easy to review, and MUST NOT completely reformulate a system in a single commit.
- Outline currency: The integration status outline MUST reflect the state of all branches, related issues, PRs, and dates, and MUST be updated after changes are committed — PR URLs SHOULD be checked first to catch new feedback.
- Non-interactive git: Git operations MUST be non-interactive using `GIT_EDITOR=true` and `GIT_PAGER=cat` to avoid vim/editor prompts.
- Issues: Most branches MAY have related upstream issues; related issues SHOULD be listed in the outline.
- Sections: Feature and fix branches should be in the correct outline sections.
- Secondary patches: Secondary patches are small fixes that either (a) resolve a residual problem that only became visible after a larger fix landed, or (b) are a prerequisite that a main fix branch depends on. They MUST be tracked in the Secondary Patches section of the outline, with a `Depends-on` or `Resolves-residual-from` note linking them to the related primary branch.
- Secondary patch upstream: A secondary patch SHOULD be submitted upstream independently if it stands alone; if it only makes sense in context of the primary fix, it MAY be folded into that PR.
- Dates: Dates for branch creation, last PR comment, and last update MUST be recorded in the status outline.
- Standalone branches: Each feature/fix branch SHOULD work standalone without depending on other local branches (except where noted).
- History: Feature/fix branch history MUST NOT be rewritten (no squash, no interactive rebase) without explicit permission from Milkii. "Complete" means the upstream PR has been merged or the branch has been deliberately closed. The `integrated` branch MAY have merge commits.
- No cherry-pick: ALWAYS use `git merge` to bring branches into `integrated`, NEVER `git cherry-pick` — cherry-picking creates duplicate commits with different SHAs, severs the branch relationship, makes bisect/revert unreliable, and hides what is actually in the build from `git log`.
- Dependencies: Any fix or feature branch that relies on another local branch MUST be noted in the Branch Dependencies section.
- PR flow: PRs SHOULD be submitted to `mxmilkiib/Carla`, and Milkii will create a further PR from there to `falktx/Carla`.
- Merged cleanup: Once the PR is fully merged into `falktx/Carla`, the branch entry MUST be moved to the "Merged to Upstream" section of the outline and its `[x]` marker removed, so it is excluded from future integration rebuilds.
- Last updated: The "Last updated" date at the top of this file MUST be updated whenever this file is edited.
- Gist sync: If this file is updated, it MUST be synced to Gist: run `gh gist edit 9c883e2022e978d9098311cbe4e2f875 --filename INTEGRATION.md INTEGRATION.md` from `/home/milkii/media/projects/cascade/carla/` (`--filename` targets the gist file, the positional arg supplies the local content).
- Commit messages: Commit messages must not be too verbose, and should be concise and descriptive.
- Conflict resolution: When resolving merge conflicts — whether during rebases or integration merges — conflicts MUST be resolved and the operation continued non-interactively.
- Code quality: Code quality MUST be verified before pushing — C++ code MUST follow Carla/JUCE coding style; Python code SHOULD pass pylint without new warnings.
- Push permission: Permission MUST be sought from the user before pushing commits to GitHub. Once the user has confirmed a push in a session, further pushes in that same session MAY proceed without asking again, to reduce friction.
- Local-only backup: All local branches MUST be pushed to `origin` (`mxmilkiib/Carla`) for off-machine backup, even if they will never be PRed upstream.

## Branch Hygiene

CRITICAL: Feature branches MUST only contain commits belonging to their named feature.

- NEVER commit `INTEGRATION.md`, integration merge commits, or unrelated fixups into a feature branch.
- `INTEGRATION.md` MUST NOT be committed to any feature branch.
- Before making any edit on a feature branch, confirm the active branch:
  ```
  git -C /home/milkii/media/projects/cascade/carla branch --show-current
  ```
- To verify a branch is clean (only its own commits ahead of `upstream/main`):
  ```
  git -C /home/milkii/media/projects/cascade/carla log --oneline upstream/main..HEAD
  ```
- If a branch has accumulated cruft, reset it:
  - No real feature commits yet: `git reset --hard upstream/main`
  - Has real commits mixed with cruft: rebase only the feature commits onto `upstream/main`, then force-update the branch ref

### Preventing Cross-Branch Contamination

- ALWAYS create new feature branches from `upstream/main`, never from local `main` — local `main` may have `INTEGRATION.md` commits or other local-only changes:
  ```
  git fetch upstream
  git checkout -b feature/<branch-name> upstream/main
  ```
- Before committing WIP, verify the branch is correct AND that the diff contains only changes belonging to that feature:
  ```
  git diff --stat
  git branch --show-current
  ```
- Before opening or updating a PR, verify the branch contains only its own commits relative to `upstream/main`:
  ```
  git log --oneline feature/<branch-name> --not upstream/main
  ```

## Directory Structure

```
/home/milkii/media/projects/cascade/carla/
  main        ← fast-forward mirror of upstream/main
  integrated  ← combined bleeding-edge build branch
  feature/*   ← individual feature/fix branches
```

### Branch Dependencies

None currently. If a branch depends on another local branch, it MUST be listed here and noted in the outline entry.

Branches with dependencies on other local branches cannot be submitted upstream as-is. They MUST be refactored to remove the dependency, or the dependency MUST be upstreamed first.

## Branch and Integration Status Outline

**Summary**: 0 need attention, 0 awaiting review, 0 local-only, 0 secondary patches, 14 upstream PRs merged to integrated, 0 merged upstream

Integration built 2026-03-27: merged all 14 open upstream PRs (#1397 port-groups, #1426 python-compileall, #1483 disconnect-group, #1483 unordered-events, #1555 handle-events, #1658 sigusr2-bridge, #1690 meson-build, #1734 pyqt-import-fix, #1748 pipewire-connections, #1975 vst-param-align, #1987 cygwin-fix, #2010 rack-ui-rework, #2011 osc-named-plugins, #2020 param-labels); fixed two build errors (d_msleep, DISTRHO::String::buffer()); build clean.

### Upstream PRs in Integration (merged to integrated, not yet to upstream/main)

These are upstream PRs that have been merged into `integrated` for local use. They are NOT local branches — they are tracked PR branches. They do not need rebasing, but MUST be re-merged if the `integrated` branch is rebuilt.

- [x] **pr-1397** — port groups canvas (26 commits) — merged 2026-03-27
- [x] **pr-1426** — compile Python files to `__pycache__` on install — merged 2026-03-27
- [x] **pr-1483** — disconnect-all-of-group patchbay menu item — merged 2026-03-27
- [x] **pr-1555** — handle unordered add/position-change events — merged 2026-03-27
- [x] **pr-1658** — SIGUSR2 handler in bridge plugin to re-load state — merged 2026-03-27
- [x] **pr-1690** — meson build config for host plugin and discovery — merged 2026-03-27
- [x] **pr-1734** — PyQt 5.15.8 `PYQT_VERSION_STR` import fix — merged 2026-03-27
- [x] **pr-1748** — fix empty connections bug on PipeWire — merged 2026-03-27
- [x] **pr-1834** — open recent file menu — merged 2026-03-27
- [x] **pr-1975** — VST params UI: left-align param titles — merged 2026-03-27
- [x] **pr-1987** — fix support for CYGWIN — merged 2026-03-27
- [x] **pr-2010** — rack UI rework (jpka import) — merged 2026-03-27
- [x] **pr-2011** — OSC: address plugins by name — merged 2026-03-27
- [x] **pr-2020** — parameter labels when running as plugin — merged 2026-03-27

### Needs Attention (CHANGES_REQUESTED)

(none)

### Secondary Patches

(none)

### Open PRs (REVIEW_REQUIRED)

(none yet)

### Local Only (No PR)

(none yet)

### Merged to Upstream

(none yet — all local feature work is pending)

---

## TODO Summary

- Needs Attention (0 branches): (none)
- Awaiting Review (0 branches): (none)
- Local Development (0 branches): (none)
- Secondary Patches (0 branches): (none)

See **Feature Request Branch TODO** section at the end of this file for planned work.

## Testing Checklist (Before Pushing to PR upstream)

Pre:
- [ ] Branch rebased on latest `falktx/Carla` main

During:
- [ ] Builds without errors (`make -j$(nproc --ignore=2)`)
- [ ] No new compiler warnings or pylint regressions
- [ ] Basic functionality tested

Post:
- [ ] No regressions in related features

## Batch Branch Update Process

This process updates all local feature/fix branches to latest upstream:

- Upstream MUST be fetched first: `git fetch upstream`
- For each feature branch:
  - The branch MUST be rebased on `upstream/main`: `git rebase upstream/main`
  - Conflicts MUST be resolved if any occur
  - The rebased branch SHOULD be force-pushed to origin: `git push --force-with-lease origin HEAD`
  - The "Rebased" date in `INTEGRATION.md` MUST be updated
- Branches with unresolved conflicts SHOULD be noted for later attention
- After all branches are updated, the Integration Merge Process SHOULD be run

## Integration Merge Process

This process merges all `[x]` marked branches into the `integrated` branch for a combined build.

### Steps

1. Commit pending `INTEGRATION.md` changes (if any) before starting:
   ```
   git add INTEGRATION.md && git commit -m "update INTEGRATION.md before integration"
   ```

2. Fetch upstream:
   ```
   git fetch upstream
   ```

3. Rebase all local feature branches on `upstream/main` (skip upstream PR branches — they are not rebased).

4. Checkout the `integrated` branch:
   ```
   git checkout integrated
   ```

5. Merge `upstream/main` into `integrated` (merge, not rebase, to preserve integration history):
   ```
   git merge upstream/main
   ```

6. Re-fetch upstream PR branches:
   ```
   git fetch upstream '+refs/pull/*/head:refs/remotes/pr/*'
   ```

7. Merge each `[x]` upstream PR branch:
   ```
   git merge --no-ff pr-<N> -m "Merge PR #<N>: <title>"
   ```

8. Merge each `[x]` local feature branch:
   ```
   git merge --no-ff origin/<branch-name>
   ```

9. Resolve merge conflicts carefully. Common issues:
   - Qt import blocks: keep the `qt_compat` version supporting both PyQt5 and PyQt6
   - C++ callback signatures: keep the newer/more complete version
   - Action constants in `patchcanvas/__init__.py`: preserve existing constants and insert new ones after, renumbering the rest

10. Update `INTEGRATION.md`:
    - Change `[ ]` to `[x]` for newly merged branches
    - Update "Rebased" and "Updated" dates to today
    - Update the summary line counts
    - Update the "Last updated" date at the top

11. Build and verify:
    ```
    make -C /home/milkii/media/projects/cascade/carla -j$(nproc --ignore=2)
    ```
    Full clean rebuild (when Makefile or new source files are involved):
    ```
    make -C /home/milkii/media/projects/cascade/carla clean
    make -C /home/milkii/media/projects/cascade/carla -j$(nproc --ignore=2)
    ```
    Basic functionality SHOULD be tested after build.

12. Sync to Gist (if `INTEGRATION.md` was updated):
    ```
    gh gist edit 9c883e2022e978d9098311cbe4e2f875 --filename INTEGRATION.md INTEGRATION.md
    ```

## Checking PR Status

```
gh pr view <PR-number> --repo falktx/Carla
gh pr list --repo falktx/Carla --author mxmilkiib
gh issue list --repo falktx/Carla --author mxmilkiib
```

## Outline Format Reference

This section documents the structure of this file for AI assistants and future maintainers.

### Branch Entry Format

Branch naming convention: `feature/YYYY.MMmon.DD-thing-descriptive-title`

```
- [x] **branch-name** - [#PR](url) - STATUS - Issue: [#ISSUE](url) - Optional description - Created: YYYY-MM-DD, Last comment: YYYY-MM-DD, Rebased: YYYY-MM-DD, Updated: YYYY-MM-DD - Next: Action item - Specifics: - Details about the branch and what probably should happen next
```

- `[x]` = merged to integration, `[ ]` = not merged
- Branch name in bold
- Issue link to related Carla issue/feature request (if applicable)
- Created date required for all branches
- Last comment date shows most recent PR comment ("none" if no comments), only for PRs
- Rebased date shows when branch was last rebased on `falktx/Carla` main ("none" if never)
- Updated date tracks last modification to branch
- Next action describes what needs to be done for this branch
- Within each section: `[x]` (integrated) branches first, then `[ ]` (not integrated) branches
- Within each group (`[x]` or `[ ]`), sort by updated date (newest first)
- STATUS is one of: `DRAFT`, `REVIEW_REQUIRED`, `CHANGES_REQUESTED`, `MERGED`, `LOCAL_ONLY`
- Secondary patch entries use `Resolves-residual-from` or `Depends-on` instead of `Issue` to link to the primary branch

### Section Order

1. Upstream PRs in Integration
2. Needs Attention (CHANGES_REQUESTED)
3. Secondary Patches
4. Open PRs (REVIEW_REQUIRED)
5. Local Only (No PR)
6. Merged to Upstream

### Summary Line

When updating integration: Update the "Last updated" date at the top of this file.
Update the summary line at the top when adding/removing branches:

```
**Summary**: X need attention, Y awaiting review, Z local-only, W secondary patches, V upstream PRs in integrated, U merged upstream
```

---

## Feature Request Branch TODO

Open issues filed by mxmilkiib on `falktx/Carla`. These are candidates for feature/fix branches to be PRed to `mxmilkiib/Carla` first. Items marked 🟢 are most feasible for standalone branches. Items marked 🟡 are possible but need scoping. Items marked 🔴 are architectural/discussion topics unlikely to result in a simple branch.

### Patchbay / Canvas

- [ ] 🟢 **[#1577](https://github.com/falktx/Carla/issues/1577) — Patchbay: scroll canvas in direction of drag**
  - When click-dragging in the patchbay, the canvas should scroll if the cursor approaches an edge.
  - Scope: Python, `source/frontend/patchcanvas/scene.py` — `mouseMoveEvent` + rubberband logic.
  - Suggested branch: `feature/YYYY.MMmon.DD-patchbay-drag-scroll`

- [ ] 🟢 **[#1481](https://github.com/falktx/Carla/issues/1481) — Default canvas size too small for imported projects**
  - On project load, the canvas should expand to fit the loaded graph if it exceeds the default size.
  - Scope: Python, `source/frontend/patchcanvas/` — initial canvas bounds / `setSceneRect`.
  - Suggested branch: `feature/YYYY.MMmon.DD-patchbay-canvas-autosize`

- [ ] 🟡 **[#1353](https://github.com/falktx/Carla/issues/1353) — Display sub carla-rack contents in Patchbay representation**
  - When a Carla-Rack is loaded as a plugin, its internal plugins should be visible in the patchbay.
  - Scope: Backend + frontend; would likely need a new patchbay API call. Non-trivial.
  - Suggested branch: `feature/YYYY.MMmon.DD-patchbay-rack-expansion`

### UI / Settings

- [ ] 🟢 **[#1499](https://github.com/falktx/Carla/issues/1499) — Display URI of missing plugin clients in log**
  - When a plugin cannot be found, its URI should appear in the error log to aid debugging.
  - Scope: C++, engine/backend — plugin loading failure path.
  - Suggested branch: `feature/YYYY.MMmon.DD-log-missing-plugin-uri`

- [ ] 🟢 **[#1482](https://github.com/falktx/Carla/issues/1482) — Option to set DSP Rate bar refresh frequency**
  - Add a setting to control how frequently the DSP usage bar refreshes.
  - Scope: Python/settings, `source/frontend/carla_host.py` + settings dialog.
  - Suggested branch: `feature/YYYY.MMmon.DD-dsp-bar-refresh-rate`

- [ ] 🟡 **[#1523](https://github.com/falktx/Carla/issues/1523) — Option to embed plugin UIs as a tab in Carla**
  - Plugin UIs should optionally open embedded in a tab inside the main Carla window rather than floating.
  - Scope: Frontend + bridge UI infrastructure; non-trivial windowing work.
  - Suggested branch: `feature/YYYY.MMmon.DD-embed-plugin-ui-tab`

- [ ] 🟡 **[#1559](https://github.com/falktx/Carla/issues/1559) — Ability to select alternative LV2 UIs**
  - When an LV2 plugin offers multiple UI types, Carla should allow the user to choose which one to use.
  - Scope: C++, `source/backend/plugin/CarlaPluginLV2.cpp` + settings dialog.
  - Suggested branch: `feature/YYYY.MMmon.DD-lv2-ui-selection`

### JACK / PipeWire / System Integration

- [ ] 🟡 **[#1576](https://github.com/falktx/Carla/issues/1576) — Option to display JACK app metadata icons**
  - JACK clients that expose icons via metadata (JACK metadata API) should have those icons displayed in the patchbay.
  - Scope: C++ JACK engine + Python patchbay; requires JACK metadata API.
  - Suggested branch: `feature/YYYY.MMmon.DD-jack-metadata-icons`

- [ ] 🟡 **[#1368](https://github.com/falktx/Carla/issues/1368) — Ability to set PipeWire client volumes**
  - Carla should expose PipeWire-level volume control for connected clients via its patchbay.
  - Scope: C++ JACK/PipeWire engine layer; depends on PipeWire-specific APIs.
  - Suggested branch: `feature/YYYY.MMmon.DD-pipewire-client-volumes`

- [ ] 🔴 **[#1533](https://github.com/falktx/Carla/issues/1533) — WSL2 bridge for Linux plugin use on Windows**
  - Run Linux plugins on Windows via a WSL2 bridge.
  - Scope: Entirely new bridge infrastructure; very large, platform-specific. Not a candidate for a simple branch.

### Meta / Discussion

- [ ] 🔴 **[#1888](https://github.com/falktx/Carla/issues/1888) — Parity and future of Carla in relation to mod-***
  - Discussion issue about architectural direction. Not actionable as a code branch.

- [ ] 🔴 **[#1620](https://github.com/falktx/Carla/issues/1620) — Add GH issue templates**
  - Repo governance task for `falktx/Carla`, not a code feature. Could be done on `mxmilkiib/Carla` fork independently if desired.
