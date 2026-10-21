from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from todolib.bridge import BridgeError
from todolib.cache import Cache
from todolib.models import Collection, Tag, Task, fold
from todolib.router import FOCUSES, MARKER, TAGS, Route, parse

INDEX_KEY = "tasks"
INDEX_MAX_AGE_SECONDS = 300
TASK_LIMIT = 100
SEARCH_LIMIT = 50
CRUMB = " › "  # noqa: RUF001
SEPARATOR = " ・ "
NO_TAG = "none"
RERUN_SECONDS = 1

FOCUS_TITLES = {
    "today": "Today",
    "starred": "Starred",
    "scheduled": "Scheduled",
    "all": "All",
    "done": "Done",
}
FOCUS_SUBTITLES = {
    "today": "Due today and overdue",
    "starred": "Starred tasks",
    "scheduled": "Tasks with a start date",
    "all": "Every task",
    "done": "Completed tasks",
}
TYPE_BADGES = {"project": "🗂️", "checklist": "☑️"}
NOTE_HINT = "⇧ Show note"
NOTE_SUBTITLE = 200
COLLECTION_SUBTITLES = {"list": "List", "smart": "Smart list"}
ACTIONS = {
    "open_task": ("open_task", "task_id", True),
    "complete_task": ("complete_task", "task_id", False),
    "uncomplete_task": ("uncomplete_task", "task_id", False),
    "delete_task": ("delete_task", "task_id", False),
    "select_list": ("select_list", "list_id", True),
    "select_smart_list": ("select_smart_list", "smart_list_id", True),
    "select_focus": ("select_focus", "focus", True),
}
SELECT_ACTIONS = {"list": "select_list", "smart": "select_smart_list"}


class TaskSource(Protocol):
    def collections(self) -> list[Collection]: ...
    def tasks(self, arguments: dict[str, Any]) -> list[Task]: ...
    def task(self, task_id: str) -> Task: ...
    def subtasks(self, task_id: str) -> list[Task]: ...
    def task_index(self) -> list[dict[str, Any]]: ...
    def tags(self) -> list[Tag]: ...
    def perform(self, command: str, arguments: dict[str, Any], ui: bool) -> None: ...


@dataclass(frozen=True)
class Deps:
    bridge: TaskSource
    cache: Cache
    refresh: Callable[[], None]


def _icon(name: str) -> dict[str, str]:
    return {"path": f"icons/{name}.png"}


def _notice(title: str, subtitle: str, icon: str) -> dict[str, Any]:
    return {"title": title, "subtitle": subtitle, "valid": False, "icon": _icon(icon)}


def _open_mod(subtitle: str, action: str, target: str) -> dict[str, Any]:
    return {
        "valid": True,
        "subtitle": subtitle,
        "variables": {"action": action, "target": target},
    }


def _drill(path: str, ref: str) -> str:
    return f"{path} {MARKER} {ref} ".lstrip()


def _task_icon(task: Task) -> str:
    if task.is_parent:
        return task.task_type
    if task.completed:
        return "task_completed"
    return "task_due" if task.due else "task"


def _task_subtitle(task: Task) -> str:
    place = f"📁 {task.list_title}" if task.list_title else ""
    if task.parent:
        place = f"{place}{CRUMB}{task.parent.title}".strip()
    parts = [place]
    if task.is_parent:
        parts.append(f"{TYPE_BADGES[task.task_type]} {task.child_count} tasks")
    if task.start:
        parts.append(f"⏳ {task.start}")
    if task.due:
        parts.append(f"📅 {task.due}")
    if task.tags:
        parts.append("🏷️ " + ", ".join(task.tags))
    if task.notes.strip():
        parts.append(NOTE_HINT)
    return SEPARATOR.join(part for part in parts if part)


def _note_mod(notes: str) -> dict[str, Any]:
    flat = " ".join(notes.split())
    if not flat:
        return {"valid": False, "subtitle": "No note"}
    if len(flat) > NOTE_SUBTITLE:
        flat = flat[:NOTE_SUBTITLE] + "…"
    return {"valid": True, "subtitle": flat, "arg": notes, "variables": {}}


def _task_item(task: Task, here: str, path: str) -> dict[str, Any]:
    title = f"🔴 {task.title}" if task.overdue else task.title
    toggle = "uncomplete_task" if task.completed else "complete_task"
    item: dict[str, Any] = {
        "title": title,
        "subtitle": _task_subtitle(task),
        "arg": task.task_id,
        "autocomplete": here,
        "valid": True,
        "variables": {"action": "open_task", "target": task.task_id},
        "icon": _icon(_task_icon(task)),
        "mods": {
            "cmd": _open_mod(
                "Mark as not completed" if task.completed else "Complete",
                toggle,
                task.task_id,
            ),
            "shift": _note_mod(task.notes),
            "ctrl": _open_mod("Delete", "delete_task", task.task_id),
            "alt": _open_mod("Open in 2Do", "open_task", task.task_id),
        },
    }
    if task.is_parent:
        item["valid"] = False
        item["autocomplete"] = _drill(path, f"task:{task.task_id}")
    return item


def _task_items(tasks: list[Task], here: str, path: str) -> list[dict[str, Any]]:
    return [_task_item(task, here, path) for task in tasks]


def _header(item: dict[str, Any], back: str) -> dict[str, Any]:
    return item | {"autocomplete": f"{back} ".lstrip(), "valid": True}


def _focus_row(focus: str) -> dict[str, Any]:
    return {
        "title": FOCUS_TITLES[focus],
        "subtitle": FOCUS_SUBTITLES[focus],
        "autocomplete": f"{focus} ",
        "valid": False,
        "icon": _icon(focus),
        "mods": {"alt": _open_mod("Open in 2Do", "select_focus", focus)},
    }


def _collection_row(collection: Collection, path: str) -> dict[str, Any]:
    return {
        "title": collection.title,
        "subtitle": COLLECTION_SUBTITLES[collection.kind],
        "autocomplete": _drill(path, f"{collection.kind}:{collection.entity}"),
        "valid": False,
        "icon": _icon("smart_list" if collection.kind == "smart" else "list"),
        "mods": {
            "alt": _open_mod(
                "Open in 2Do", SELECT_ACTIONS[collection.kind], collection.entity
            )
        },
    }


def _search_arguments(route: Route, **arguments: Any) -> dict[str, Any]:
    if route.text:
        arguments["search"] = route.text
    return arguments


def _menu(route: Route, deps: Deps) -> list[dict[str, Any]]:
    wanted = fold(route.text)
    rows = [
        _focus_row(focus)
        for focus in FOCUSES
        if not wanted or wanted in fold(FOCUS_TITLES[focus])
    ]
    if not wanted or wanted in fold("Tags"):
        rows.append(_tags_row())
    rows += [
        _collection_row(collection, route.path)
        for collection in deps.bridge.collections()
        if not wanted or wanted in fold(collection.title)
    ]
    return rows


def _focus(route: Route, here: str, deps: Deps) -> list[dict[str, Any]]:
    done = route.entity == "done"
    tasks = deps.bridge.tasks(
        _search_arguments(
            route, focus=route.entity, include_completed=done, limit=TASK_LIMIT
        )
    )
    items = _task_items(tasks, here, route.path)
    if route.path.casefold().split()[:1] != [route.entity]:
        return items
    header = _header(_focus_row(route.entity), "") | {
        "variables": {"action": "select_focus", "target": route.entity},
        "subtitle": "Open in 2Do",
    }
    return [header, *items]


def _collection(route: Route, here: str, deps: Deps) -> list[dict[str, Any]]:
    key = "smart_list_id" if route.kind == "smart" else "list_id"
    tasks = deps.bridge.tasks(
        _search_arguments(
            route, **{key: route.entity}, include_completed=False, limit=TASK_LIMIT
        )
    )
    items = _task_items(tasks, here, route.path)
    collection = next(
        (
            collection
            for collection in deps.bridge.collections()
            if collection.kind == route.kind and collection.entity == route.entity
        ),
        None,
    )
    if collection is None:
        return items
    header = _header(_collection_row(collection, route.parent), route.parent) | {
        "variables": {"action": SELECT_ACTIONS[route.kind], "target": route.entity},
        "subtitle": f"{COLLECTION_SUBTITLES[route.kind]}{SEPARATOR}Open in 2Do",
    }
    return [header, *items]


def _parent(route: Route, here: str, deps: Deps) -> list[dict[str, Any]]:
    parent = deps.bridge.task(route.entity)
    header = _header(_task_item(parent, here, route.parent), route.parent)
    subtasks = [
        task
        for task in deps.bridge.subtasks(route.entity)
        if not route.text or task.matches(route.text)
    ]
    return [header, *_task_items(subtasks, here, route.path)]


def _indexed_tasks(deps: Deps) -> list[Task] | None:
    hit = deps.cache.read(INDEX_KEY, INDEX_MAX_AGE_SECONDS)
    if hit is None or hit.stale:
        deps.refresh()
    if hit is None:
        return None
    return [Task.from_dict(record) for record in hit.data]


def _loading() -> list[dict[str, Any]]:
    return [_notice("Loading tasks…", "Reading every open task from 2Do", "search")]


def _tags_row() -> dict[str, Any]:
    return {
        "title": "Tags",
        "subtitle": "Tasks by tag",
        "autocomplete": f"{TAGS} ",
        "valid": False,
        "icon": _icon("tag"),
    }


def _untagged(tasks: list[Task]) -> list[Task]:
    return [task for task in tasks if not task.tag_ids and task.parent is None]


def _tag_row(title: str, tag_id: str, count: int, subtitle: str = "") -> dict[str, Any]:
    tasks = "1 task" if count == 1 else f"{count} tasks"
    return {
        "title": title,
        "subtitle": SEPARATOR.join(part for part in (tasks, subtitle) if part),
        "autocomplete": _drill(TAGS, f"tag:{tag_id}"),
        "valid": False,
        "icon": _icon("no_tag" if tag_id == NO_TAG else "tag"),
    }


def _tags(route: Route, _here: str, deps: Deps) -> list[dict[str, Any]]:
    tasks = _indexed_tasks(deps)
    if tasks is None:
        return _loading()
    counts: dict[str, int] = {}
    for task in tasks:
        for tag_id in task.tag_ids:
            counts[tag_id] = counts.get(tag_id, 0) + 1
    wanted = fold(route.text)
    tags = sorted(
        (tag for tag in deps.bridge.tags() if not wanted or wanted in fold(tag.title)),
        key=lambda tag: (-counts.get(tag.tag_id, 0), fold(tag.title)),
    )
    rows = []
    if not wanted or wanted in fold("No tag"):
        rows.append(
            _tag_row("No tag", NO_TAG, len(_untagged(tasks)), "Top-level tasks only")
        )
    rows += [
        _tag_row(
            tag.title,
            tag.tag_id,
            counts.get(tag.tag_id, 0),
            "Paused" if tag.paused else "",
        )
        for tag in tags
    ]
    return rows


def _tag(route: Route, here: str, deps: Deps) -> list[dict[str, Any]]:
    tasks = _indexed_tasks(deps)
    if tasks is None:
        return _loading()
    if route.entity == NO_TAG:
        title, tagged = "No tag", _untagged(tasks)
    else:
        tag = next((t for t in deps.bridge.tags() if t.tag_id == route.entity), None)
        title = tag.title if tag else route.entity
        tagged = [task for task in tasks if route.entity in task.tag_ids]
    header = _header(
        _tag_row(title, route.entity, len(tagged), "Tab to go back"), route.parent
    ) | {"valid": False}
    matching = [task for task in tagged if not route.text or task.matches(route.text)]
    return [header, *_task_items(matching, here, route.path)]


def _search(route: Route, here: str, deps: Deps) -> list[dict[str, Any]]:
    if not route.text:
        return [_notice("Search 2Do", "Type to search every open task", "search")]
    tasks = deps.bridge.tasks(
        {
            "focus": "all",
            "search": route.text,
            "include_completed": False,
            "limit": SEARCH_LIMIT,
        }
    )
    seen = {task.task_id for task in tasks}
    tasks += [
        task
        for task in _indexed_tasks(deps) or []
        if task.parent and task.task_id not in seen and task.matches(route.text)
    ]
    return _task_items(tasks, here, route.path)


PAGES = {
    "focus": _focus,
    "list": _collection,
    "smart": _collection,
    "task": _parent,
    "search": _search,
    TAGS: _tags,
    "tag": _tag,
}
INDEXED_PAGES = (TAGS, "tag")


def run(query: str, mode: str, deps: Deps) -> dict[str, Any]:
    route = parse(query, mode)
    try:
        if route.kind == "menu":
            items = _menu(route, deps)
        else:
            items = PAGES[route.kind](route, query, deps)
    except BridgeError as error:
        if error.locked:
            items = [_notice("2Do is locked", "Unlock 2Do and try again", "error")]
        else:
            items = [_notice("2Do did not respond", str(error), "error")]
    if not items:
        items = [_notice("Nothing here", "No matching tasks", "empty")]
    result: dict[str, Any] = {"items": items}
    if route.kind in INDEXED_PAGES and deps.cache.read(INDEX_KEY, 10**9) is None:
        result["rerun"] = RERUN_SECONDS
    return result


def refresh(deps: Deps) -> None:
    if not deps.cache.claim_refresh(INDEX_KEY):
        return
    try:
        deps.cache.write(INDEX_KEY, deps.bridge.task_index())
    finally:
        deps.cache.release_refresh(INDEX_KEY)


def perform(action: str, target: str, deps: Deps) -> None:
    if action not in ACTIONS or not target:
        return
    command, key, ui = ACTIONS[action]
    deps.bridge.perform(command, {key: target}, ui)
    if not ui:
        deps.cache.delete(INDEX_KEY)
        refresh(deps)
