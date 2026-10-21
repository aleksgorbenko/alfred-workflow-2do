<p align="center">
  <img src="icon.png" width="128" alt="2Do for Alfred icon">
</p>

<h1 align="center">2Do for Alfred</h1>

<p align="center">Browse, open and complete 2Do tasks and lists from Alfred.</p>

<p align="center">
  <a href="https://github.com/aleksgorbenko/alfred-workflow-2do/actions/workflows/ci.yml"><img src="https://github.com/aleksgorbenko/alfred-workflow-2do/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI status"></a>
  <a href="https://github.com/aleksgorbenko/alfred-workflow-2do/releases/latest"><img src="https://img.shields.io/github/v/release/aleksgorbenko/alfred-workflow-2do?label=release&color=4c8dff" alt="Latest release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/licence-MIT-blue" alt="Licence MIT"></a>
  <img src="https://img.shields.io/badge/macOS-14%2B-black?logo=apple" alt="macOS 14 or later">
  <a href="https://www.alfredapp.com/powerpack/"><img src="https://img.shields.io/badge/Alfred-5%20Powerpack-5c1f87" alt="Alfred 5 Powerpack"></a>
</p>

<p align="center">
  <a href="#commands">Commands</a> ·
  <a href="#install">Install</a> ·
  <a href="#development">Development</a>
</p>

Type `ls` to browse your 2Do lists and smart lists.

![2Do lists and smart lists in Alfred](images/about/lists.png)

Alfred Workflow to browse/edit [2Do](https://www.2doapp.com) tasks/lists via its AppleScript automation suite.

Requires 2Do Mac (recent version with the `2Do Automation Suite` AppleScript dictionary).

## Commands

- **List lists & smart lists** - browse your normal lists and smart lists, each with its own icon. Selecting one opens it in 2Do.
- **Browse a list / smart list** - after selecting a list above, shows its uncompleted tasks immediately, narrows as you type. Open, complete, or delete from here.
- **Search all tasks** - live search (title, notes, tags, locations) across all uncompleted tasks as you type. Open, complete, or delete.
- **Today** - uncompleted tasks due today or overdue, shown immediately, narrows as you type. Open, complete, or delete.
- **Search completed tasks** - search completed tasks, for undoing an accidental complete. Open, uncomplete, or delete.

Each task row shows: 📁 list · 📅 due date · 🏷️ tags · 📝 notes (truncated), when present.

## Install

1. Download the latest `2Do.alfredworkflow` from [Releases](https://github.com/aleksgorbenko/alfred-workflow-2do/releases).
2. Double-click it - Alfred will prompt to import.
3. Requires [Alfred](https://www.alfredapp.com) with a Powerpack licence (Script Filters/Run Script require it).

## Development

- AppleScript only, no dependencies.
- `scripts/` - runtime scripts Alfred calls.
- `tools/icons.txt` - result icons, rendered by `make icons`.

```sh
make setup   # install dev tools
make ci      # everything CI runs
make check   # compile every AppleScript, lint plist and Markdown
make icons   # render icons/*.png
make build   # package dist/2Do.alfredworkflow
make release VERSION=v1.0.0
make link-live WORKFLOW_DIR=/path/to/installed/workflow
```

## My Other Workflows

- [Netlify for Alfred](https://github.com/aleksgorbenko/alfred-workflow-netlify)
- [WaniKani for Alfred](https://github.com/aleksgorbenko/alfred-workflow-wanikani)
- [BunPro for Alfred](https://github.com/aleksgorbenko/alfred-workflow-bunpro)
- [Discogs for Alfred](https://github.com/aleksgorbenko/alfred-workflow-discogs)
- [Bandcamp for Alfred](https://github.com/aleksgorbenko/alfred-workflow-bandcamp)
- [config](https://github.com/aleksgorbenko/config) - index of all my workflows, plus macOS/iOS setup
