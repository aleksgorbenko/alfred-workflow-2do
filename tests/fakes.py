import json
from typing import Any


def task_record(task_id: str, title: str, **fields: Any) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "title": title,
        "task_type": "normal",
        "list_title": "Home",
        "notes": "",
        "tags": [],
        "completed": False,
        "starred": False,
        "presentation": {"is_overdue": False},
    } | fields


class FakeRunner:
    def __init__(self, *replies: list[dict[str, Any]]):
        self.replies = list(replies)
        self.requests: list[list[dict[str, Any]]] = []

    def __call__(self, args: list[str]) -> str:
        self.requests.append(json.loads(args[1]))
        return json.dumps(self.replies.pop(0))
