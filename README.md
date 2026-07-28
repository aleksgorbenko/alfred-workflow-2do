# alfred-workflow-2do

Alfred Workflow to browse/edit [2Do](https://www.2doapp.com) tasks/lists via its AppleScript automation suite.

Requires 2Do Mac (recent version with the `2Do Automation Suite` AppleScript dictionary).

## Commands

- **List lists & smart lists** — browse your normal lists (📁) and smart lists (⚙️). Selecting one opens it in 2Do.
- **Browse a list / smart list** — after selecting a list above, shows its uncompleted tasks immediately, narrows as you type. Open, complete, or delete from here.
- **Search all tasks** — live search (title, notes, tags, locations) across all uncompleted tasks as you type. Open, complete, or delete.
- **Today** — uncompleted tasks due today or overdue, shown immediately, narrows as you type. Open, complete, or delete.
- **Search completed tasks** — search completed tasks, for undoing an accidental complete. Open, uncomplete, or delete.

Each task row shows: 📁 list · 📅 due date · 🏷️ tags · 📝 notes (truncated), when present.

## Install

1. Download the latest `2Do.alfredworkflow` from [Releases](https://github.com/aleksgorbenko/alfred-workflow-2do/releases).
2. Double-click it — Alfred will prompt to import.
3. Requires [Alfred](https://www.alfredapp.com) with a Powerpack license (Script Filters/Run Script require it).
