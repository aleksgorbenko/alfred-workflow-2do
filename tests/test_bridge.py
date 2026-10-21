from pathlib import Path

import pytest
from fakes import FakeRunner, task_record

from todolib.bridge import Bridge, BridgeError, run_osascript
from todolib.models import Collection, Tag

SCRIPT = Path("bridge.js")


def test_collections_reads_lists_and_smart_lists():
    runner = FakeRunner(
        [
            {"result": {"list": [{"list_id": "l1", "title": "Home"}]}},
            {"result": {"smart_lists": [{"smart_list_id": "s1", "title": "Inbox"}]}},
        ]
    )
    assert Bridge(runner, SCRIPT).collections() == [
        Collection("list", "l1", "Home"),
        Collection("smart", "s1", "Inbox"),
    ]
    assert [request["command"] for request in runner.requests[0]] == [
        "list_lists",
        "list_smart_lists",
    ]


def test_tasks_sends_a_query():
    runner = FakeRunner([{"result": [task_record("t1", "Milk")]}])
    tasks = Bridge(runner, SCRIPT).tasks({"focus": "today"})
    assert [task.title for task in tasks] == ["Milk"]
    assert runner.requests[0] == [
        {"op": "tasks", "command": "query_tasks", "arguments": {"focus": "today"}}
    ]


def test_task_reads_one_task():
    runner = FakeRunner([{"result": [task_record("p1", "Move")]}])
    assert Bridge(runner, SCRIPT).task("p1").task_id == "p1"


def test_subtasks_skip_completed():
    runner = FakeRunner([{"result": [task_record("c1", "Pack")]}])
    assert [task.task_id for task in Bridge(runner, SCRIPT).subtasks("p1")] == ["c1"]
    assert runner.requests[0][0]["arguments"] == {
        "task_id": "p1",
        "include_completed": False,
    }


def test_task_index_returns_records():
    runner = FakeRunner([{"result": [task_record("c1", "Pack")]}])
    assert Bridge(runner, SCRIPT).task_index()[0]["task_id"] == "c1"
    assert runner.requests[0] == [{"op": "task_index"}]


def test_tags_reads_tags():
    runner = FakeRunner(
        [{"result": {"tags": [{"tag_id": "g1", "title": "home", "paused": True}]}}]
    )
    assert Bridge(runner, SCRIPT).tags() == [Tag("g1", "home", paused=True)]


def test_perform_marks_ui_commands():
    runner = FakeRunner([{"result": {}}], [{"result": {}}])
    bridge = Bridge(runner, SCRIPT)
    bridge.perform("open_task", {"task_id": "t1"}, ui=True)
    bridge.perform("complete_task", {"task_id": "t1"}, ui=False)
    assert runner.requests[0][0]["op"] == "ui"
    assert "op" not in runner.requests[1][0]


def test_reply_error_raises():
    runner = FakeRunner([{"error": "access_denied: 2Do is locked"}])
    with pytest.raises(BridgeError) as raised:
        Bridge(runner, SCRIPT).tasks({})
    assert raised.value.locked


def test_run_osascript_returns_output(monkeypatch):
    class Completed:
        returncode = 0
        stdout = "[]"
        stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *_args, **_kwargs: Completed())
    assert run_osascript(["x"]) == "[]"


def test_run_osascript_failure_raises(monkeypatch):
    class Completed:
        returncode = 1
        stdout = ""
        stderr = "execution error"

    monkeypatch.setattr("subprocess.run", lambda *_args, **_kwargs: Completed())
    with pytest.raises(BridgeError, match="execution error"):
        run_osascript(["x"])
