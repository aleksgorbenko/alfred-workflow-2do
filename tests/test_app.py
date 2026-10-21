from pathlib import Path
from typing import Any

import pytest
from fakes import task_record

from todolib.app import CRUMB, INDEX_KEY, SEPARATOR, Deps, perform, refresh, run
from todolib.bridge import BridgeError
from todolib.cache import Cache
from todolib.models import Collection, Tag, Task

HOME = Collection("list", "l1", "Home")
INBOX = Collection("smart", "s1", "Inbox")
MILK = Task.from_dict(task_record("t1", "Buy milk", due_date="2026-10-21"))
LATE = Task.from_dict(task_record("t2", "Pay rent", presentation={"is_overdue": True}))
MOVE = Task.from_dict(
    task_record("p1", "Move house", task_type="project", child_task_ids=["c1", "c2"])
)
BOXES = task_record(
    "c1",
    "Pack boxes",
    parent={"task_id": "p1", "title": "Move house", "task_type": "project"},
)


ERRAND = Tag("g1", "errand")
PAUSED = Tag("g2", "someday", paused=True)
TAGGED = task_record("t6", "Post letter", tags=[{"tag_id": "g1", "title": "errand"}])
UNTAGGED = task_record("t7", "Water plants")


class FakeSource:
    def __init__(self, tasks: list[Task] | None = None, error: str = ""):
        self.listed = tasks or []
        self.error = error
        self.queries: list[dict[str, Any]] = []
        self.performed: list[tuple[str, dict[str, Any], bool]] = []

    def _check(self) -> None:
        if self.error:
            raise BridgeError(self.error)

    def collections(self) -> list[Collection]:
        self._check()
        return [HOME, INBOX]

    def tasks(self, arguments: dict[str, Any]) -> list[Task]:
        self._check()
        self.queries.append(arguments)
        return self.listed

    def task(self, task_id: str) -> Task:
        assert task_id == "p1"
        return MOVE

    def subtasks(self, task_id: str) -> list[Task]:
        assert task_id == "p1"
        return [Task.from_dict(BOXES), Task.from_dict(task_record("c2", "Book van"))]

    def task_index(self) -> list[dict[str, Any]]:
        return [BOXES]

    def tags(self) -> list[Tag]:
        return [ERRAND, PAUSED]

    def perform(self, command: str, arguments: dict[str, Any], ui: bool) -> None:
        self.performed.append((command, arguments, ui))


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def cache(tmp_path: Path) -> Cache:
    return Cache(tmp_path, Clock())


def deps_for(source: FakeSource, cache: Cache, refreshes: list[int] | None = None):
    calls = refreshes if refreshes is not None else []
    return Deps(source, cache, lambda: calls.append(1))


def titles(result: dict[str, Any]) -> list[str]:
    return [item["title"] for item in result["items"]]


def test_menu_lists_focuses_then_collections(cache):
    result = run("", "browse", deps_for(FakeSource(), cache))
    assert titles(result) == [
        "Today",
        "Starred",
        "Scheduled",
        "All",
        "Done",
        "Tags",
        "Home",
        "Inbox",
    ]


def test_menu_filters_by_title(cache):
    assert titles(run("inb", "browse", deps_for(FakeSource(), cache))) == ["Inbox"]


def test_menu_collection_drills_into_a_path(cache):
    items = run("", "browse", deps_for(FakeSource(), cache))["items"]
    assert items[6]["autocomplete"] == "> list:l1 "
    assert items[7]["mods"]["alt"]["variables"] == {
        "action": "select_smart_list",
        "target": "s1",
    }


def test_focus_page_has_a_header_that_goes_back(cache):
    source = FakeSource([MILK])
    items = run("today ", "browse", deps_for(source, cache))["items"]
    assert items[0]["title"] == "Today"
    assert items[0]["autocomplete"] == ""
    assert items[0]["variables"] == {"action": "select_focus", "target": "today"}
    assert source.queries == [
        {"focus": "today", "include_completed": False, "limit": 100}
    ]


def test_focus_page_passes_the_search(cache):
    source = FakeSource([MILK])
    run("starred milk", "browse", deps_for(source, cache))
    assert source.queries[0]["search"] == "milk"


def test_done_includes_completed_tasks(cache):
    source = FakeSource([])
    run("", "done", deps_for(source, cache))
    assert source.queries[0]["include_completed"] is True


def test_today_keyword_has_no_header(cache):
    assert titles(run("", "today", deps_for(FakeSource([MILK]), cache))) == ["Buy milk"]


def test_overdue_task_is_marked_red(cache):
    items = run("", "today", deps_for(FakeSource([LATE]), cache))["items"]
    assert items[0]["title"] == "🔴 Pay rent"


def test_task_row_opens_completes_and_deletes(cache):
    item = run("", "today", deps_for(FakeSource([MILK]), cache))["items"][0]
    assert item["variables"] == {"action": "open_task", "target": "t1"}
    assert item["mods"]["cmd"]["variables"]["action"] == "complete_task"
    assert item["mods"]["ctrl"]["variables"]["action"] == "delete_task"
    assert item["mods"]["shift"] == {"valid": False, "subtitle": "No note"}
    assert item["icon"]["path"] == "icons/task_due.png"
    assert item["subtitle"] == f"📁 Home{SEPARATOR}📅 2026-10-21"


def test_completed_task_can_be_uncompleted(cache):
    done = Task.from_dict(task_record("t3", "Old", completed=True))
    item = run("", "done", deps_for(FakeSource([done]), cache))["items"][0]
    assert item["mods"]["cmd"]["variables"]["action"] == "uncomplete_task"
    assert item["icon"]["path"] == "icons/task_completed.png"


def test_project_row_drills_into_its_subtasks(cache):
    item = run("today ", "browse", deps_for(FakeSource([MOVE]), cache))["items"][1]
    assert item["valid"] is False
    assert item["autocomplete"] == "today > task:p1 "
    assert item["subtitle"] == f"📁 Home{SEPARATOR}🗂️ 2 tasks"
    assert item["icon"]["path"] == "icons/project.png"


def test_project_page_shows_the_project_then_subtasks(cache):
    result = run("today > task:p1 ", "browse", deps_for(FakeSource(), cache))
    assert titles(result) == ["Move house", "Pack boxes", "Book van"]
    header = result["items"][0]
    assert header["autocomplete"] == "today "
    assert header["valid"] is True
    assert result["items"][1]["subtitle"] == f"📁 Home{CRUMB}Move house"


def test_project_page_filters_subtasks(cache):
    result = run("> task:p1 van", "browse", deps_for(FakeSource(), cache))
    assert titles(result) == ["Move house", "Book van"]


def test_list_page_has_a_header_and_queries_the_list(cache):
    source = FakeSource([MILK])
    result = run("> list:l1 ", "browse", deps_for(source, cache))
    assert titles(result) == ["Home", "Buy milk"]
    assert result["items"][0]["variables"] == {
        "action": "select_list",
        "target": "l1",
    }
    assert source.queries[0]["list_id"] == "l1"


def test_smart_list_page_queries_the_smart_list(cache):
    source = FakeSource([MILK])
    run("> smart:s1 milk", "browse", deps_for(source, cache))
    assert source.queries[0] == {
        "smart_list_id": "s1",
        "include_completed": False,
        "limit": 100,
        "search": "milk",
    }


def test_unknown_list_has_no_header(cache):
    result = run("> list:gone ", "browse", deps_for(FakeSource([MILK]), cache))
    assert titles(result) == ["Buy milk"]


def test_empty_search_shows_a_hint(cache):
    assert titles(run("", "search", deps_for(FakeSource(), cache))) == ["Search 2Do"]


def test_search_without_an_index_refreshes_it(cache):
    refreshes: list[int] = []
    result = run("pack", "search", deps_for(FakeSource([MILK]), cache, refreshes))
    assert titles(result) == ["Buy milk"]
    assert refreshes == [1]


def test_search_merges_matching_subtasks_with_their_parent(cache):
    cache.write(INDEX_KEY, [BOXES])
    refreshes: list[int] = []
    result = run("pack", "search", deps_for(FakeSource([MILK]), cache, refreshes))
    assert titles(result) == ["Buy milk", "Pack boxes"]
    assert result["items"][1]["subtitle"] == f"📁 Home{CRUMB}Move house"
    assert refreshes == []


def test_search_drills_into_a_project_and_back(cache):
    result = run("move > task:p1 ", "search", deps_for(FakeSource(), cache))
    assert result["items"][0]["autocomplete"] == "move "


def test_locked_2do_shows_a_notice(cache):
    source = FakeSource(error="access_denied: locked")
    assert titles(run("", "browse", deps_for(source, cache))) == ["2Do is locked"]


def test_other_errors_show_the_message(cache):
    source = FakeSource(error="boom")
    result = run("", "browse", deps_for(source, cache))
    assert result["items"][0]["subtitle"] == "boom"


def test_nothing_found_shows_a_notice(cache):
    assert titles(run("", "today", deps_for(FakeSource(), cache))) == ["Nothing here"]


def test_refresh_writes_the_subtask_index(cache):
    refresh(deps_for(FakeSource(), cache))
    hit = cache.read(INDEX_KEY, 300)
    assert hit is not None
    assert hit.data == [BOXES]


def test_refresh_skips_when_another_refresh_runs(cache):
    cache.claim_refresh(INDEX_KEY)
    refresh(deps_for(FakeSource(), cache))
    assert cache.read(INDEX_KEY, 300) is None


def test_perform_completes_and_rebuilds_the_index(cache):
    cache.write(INDEX_KEY, [TAGGED])
    source = FakeSource()
    perform("complete_task", "t1", deps_for(source, cache))
    assert source.performed == [("complete_task", {"task_id": "t1"}, False)]
    hit = cache.read(INDEX_KEY, 300)
    assert hit is not None
    assert hit.data == [BOXES]


def test_perform_opens_lists_in_2do(cache):
    source = FakeSource()
    perform("select_smart_list", "s1", deps_for(source, cache))
    assert source.performed == [("select_smart_list", {"smart_list_id": "s1"}, True)]


def test_perform_ignores_unknown_actions(cache):
    source = FakeSource()
    perform("format_disk", "x", deps_for(source, cache))
    perform("open_task", "", deps_for(source, cache))
    assert source.performed == []


def test_task_with_a_note_shows_it_on_shift(cache):
    notes = "line one\n" + "word " * 60
    noted = Task.from_dict(
        task_record("t4", "Read", tags=[{"title": "books"}], notes=notes)
    )
    item = run("", "today", deps_for(FakeSource([noted]), cache))["items"][0]
    assert item["subtitle"] == SEPARATOR.join(("📁 Home", "🏷️ books", "⇧ Show note"))
    shift = item["mods"]["shift"]
    assert shift["arg"] == notes
    assert shift["subtitle"].startswith("line one word")
    assert shift["subtitle"].endswith("…")


def test_scheduled_task_shows_its_start(cache):
    later = Task.from_dict(task_record("t5", "Call", start_date="2026-10-22"))
    item = run("", "today", deps_for(FakeSource([later]), cache))["items"][0]
    assert item["subtitle"] == f"📁 Home{SEPARATOR}⏳ 2026-10-22"


def test_tags_page_lists_no_tag_first_then_tags_by_count(cache):
    cache.write(INDEX_KEY, [TAGGED, UNTAGGED, BOXES])
    items = run("tags ", "browse", deps_for(FakeSource(), cache))["items"]
    assert [(item["title"], item["subtitle"]) for item in items] == [
        ("No tag", f"1 task{SEPARATOR}Top-level tasks only"),
        ("errand", "1 task"),
        ("someday", f"0 tasks{SEPARATOR}Paused"),
    ]
    assert items[1]["autocomplete"] == "tags > tag:g1 "


def test_tags_page_filters_tags(cache):
    cache.write(INDEX_KEY, [TAGGED])
    result = run("tags some", "browse", deps_for(FakeSource(), cache))
    assert titles(result) == ["someday"]


def test_tags_page_waits_for_the_index(cache):
    refreshes: list[int] = []
    result = run("tags ", "browse", deps_for(FakeSource(), cache, refreshes))
    assert titles(result) == ["Loading tasks…"]
    assert result["rerun"] == 1
    assert refreshes == [1]


def test_tag_page_lists_tagged_tasks_and_searches_them(cache):
    cache.write(INDEX_KEY, [TAGGED, UNTAGGED])
    result = run("tags > tag:g1 ", "browse", deps_for(FakeSource(), cache))
    assert titles(result) == ["errand", "Post letter"]
    assert result["items"][0]["autocomplete"] == "tags "
    assert result["items"][0]["valid"] is False
    filtered = run("tags > tag:g1 water", "browse", deps_for(FakeSource(), cache))
    assert titles(filtered) == ["errand"]


def test_no_tag_page_lists_untagged_top_level_tasks(cache):
    cache.write(INDEX_KEY, [TAGGED, UNTAGGED, BOXES])
    result = run("tags > tag:none ", "browse", deps_for(FakeSource(), cache))
    assert titles(result) == ["No tag", "Water plants"]


def test_tag_page_waits_for_the_index(cache):
    result = run("tags > tag:g1 ", "browse", deps_for(FakeSource(), cache))
    assert titles(result) == ["Loading tasks…"]


def test_unknown_tag_uses_its_id(cache):
    cache.write(INDEX_KEY, [])
    result = run("tags > tag:gone ", "browse", deps_for(FakeSource(), cache))
    assert titles(result) == ["gone"]
