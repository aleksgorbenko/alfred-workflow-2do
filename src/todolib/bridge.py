import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from todolib.models import Collection, Tag, Task

Runner = Callable[[list[str]], str]


class BridgeError(Exception):
    @property
    def locked(self) -> bool:
        return str(self).startswith("access_denied")


def run_osascript(args: list[str]) -> str:
    completed = subprocess.run(
        ["/usr/bin/osascript", "-l", "JavaScript", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise BridgeError(completed.stderr.strip() or "osascript failed")
    return completed.stdout


class Bridge:
    def __init__(self, runner: Runner, script: Path):
        self._runner = runner
        self._script = script

    def send(self, *requests: dict[str, Any]) -> list[Any]:
        output = self._runner([str(self._script), json.dumps(list(requests))])
        replies = json.loads(output)
        for reply in replies:
            if "error" in reply:
                raise BridgeError(reply["error"])
        return [reply["result"] for reply in replies]

    def collections(self) -> list[Collection]:
        lists, smart = self.send(
            {"command": "list_lists", "arguments": {"include_archived": False}},
            {"command": "list_smart_lists"},
        )
        return [
            *(
                Collection.from_list(r)
                for r in lists.get("lists", lists.get("list", ()))
            ),
            *(Collection.from_smart_list(r) for r in smart.get("smart_lists", ())),
        ]

    def tasks(self, arguments: dict[str, Any]) -> list[Task]:
        (records,) = self.send(
            {"op": "tasks", "command": "query_tasks", "arguments": arguments}
        )
        return [Task.from_dict(record) for record in records]

    def task(self, task_id: str) -> Task:
        (records,) = self.send(
            {"op": "tasks", "command": "get_task", "arguments": {"task_id": task_id}}
        )
        return Task.from_dict(records[0])

    def subtasks(self, task_id: str) -> list[Task]:
        (records,) = self.send(
            {
                "op": "tasks",
                "command": "list_subtasks",
                "arguments": {"task_id": task_id, "include_completed": False},
            }
        )
        return [Task.from_dict(record) for record in records]

    def task_index(self) -> list[dict[str, Any]]:
        (records,) = self.send({"op": "task_index"})
        return records

    def tags(self) -> list[Tag]:
        (result,) = self.send({"command": "list_tags"})
        return [Tag.from_dict(record) for record in result.get("tags", ())]

    def perform(self, command: str, arguments: dict[str, Any], ui: bool) -> None:
        request = {"command": command, "arguments": arguments}
        self.send({**request, "op": "ui"} if ui else request)
