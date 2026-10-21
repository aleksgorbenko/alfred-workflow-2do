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

Type `ls` to browse Today, Starred, Scheduled, All, Done, tags, your lists and smart lists.

![2Do browser in Alfred](images/about/browse.png)

Type `today` for tasks due today; overdue tasks are marked 🔴.

![2Do Today in Alfred](images/about/today.png)

Alfred Workflow for [2Do](https://www.2doapp.com) tasks, projects and checklists, via the 2Do Automation Suite.

## Commands

| Keyword | Shows |
|---|---|
| `ls` | Today, Starred, Scheduled, All, Done, lists and smart lists |
| `ls today`, `ls starred`, … | That focus list; words after it search it |
| `ls tags` | No tag first, then tags by task count; pick one to list and search its tasks |
| `to <query>` | Every open task matching title, notes or tags, subtasks included |
| `today` | Tasks due today and overdue |
| `ct` | Completed tasks |

### Navigation

- Enter or Tab on a list, smart list, project or checklist opens it in Alfred.
- The path builds up in the search box (`ls today > task:…`); delete the last part to go back.
- The first row of a page is the page itself: Enter opens it in 2Do, Tab goes back.
- Words after a path filter that page.

![2Do Starred in Alfred](images/about/starred.png)

![2Do Scheduled in Alfred](images/about/scheduled.png)

### Keys

| Key | Action |
|---|---|
| Enter | Open the task in 2Do |
| Cmd+Enter | Complete; on a completed task, mark as not completed |
| Shift | Hold to read the note; Shift+Enter shows it in Large Type |
| Ctrl+Enter | Delete |
| Alt+Enter | Open in 2Do, also for lists and focus rows |

### Rows

- Projects (🗂️) and checklists (☑️) have their own icons and show how many tasks they hold.
- Overdue tasks start with 🔴.
- Subtasks show their list and parent: `📁 Home › Move house`.
- Each row shows start date (⏳), due date (📅) and tags; `⇧ Show note` marks tasks with a note.
- `to` and tags read subtasks and tags from an index refreshed in the background every 5 minutes and after every change.
- No tag lists top-level tasks only.

## Install

1. Download the latest `2Do.alfredworkflow` from [Releases](https://github.com/aleksgorbenko/alfred-workflow-2do/releases).
2. Double-click it - Alfred will prompt to import.
3. Requires [Alfred](https://www.alfredapp.com) with a Powerpack licence.
4. Requires 2Do for Mac with the 2Do Automation Suite, unlocked.
5. Requires Python 3.11 or newer (`brew install python`).

## Development

- Python 3.11 or newer, no runtime dependencies.
- `src/todolib/` - routing and rows; `src/bridge.js` - JXA bridge to 2Do's automation commands.
- `tools/icons.txt` - result icons, rendered by `make icons`.

```sh
make setup   # install dev tools
make ci      # everything CI runs
make check   # ruff, shellcheck, JXA compile, plist, Markdown, tests (80% coverage gate)
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
