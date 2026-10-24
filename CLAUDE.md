# 2Do for Alfred

- Run every task through `make` (setup, test, lint, format, icons, build, link-live, sync-plist); never call pytest, ruff, shellcheck or uv directly.
- Code lives in `src/todolib/` (Python) and `src/bridge.js` (JXA bridge to 2Do), Alfred nodes and UI text in `info.plist`, icon sources in `tools/icons.txt`.
- Edit `info.plist` with python `plistlib`, then `make lint`; run `make sync-plist` after any edit in Alfred's UI.
- Follow `standards.md` in the `alfred-workflow` skill: modifier keys, subtitle hints, navigation, README and embedded readme.
- Use a feature branch per change; never push or merge without being asked.
