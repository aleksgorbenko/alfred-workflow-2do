import unicodedata
from dataclasses import dataclass
from typing import Any

PARENT_TYPES = ("project", "checklist")


def fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


@dataclass(frozen=True)
class Parent:
    task_id: str
    title: str
    task_type: str


@dataclass(frozen=True)
class Task:
    task_id: str
    title: str
    task_type: str
    list_title: str
    notes: str = ""
    tags: tuple[str, ...] = ()
    tag_ids: tuple[str, ...] = ()
    due: str = ""
    start: str = ""
    completed: bool = False
    starred: bool = False
    overdue: bool = False
    child_count: int = 0
    parent: Parent | None = None

    @property
    def is_parent(self) -> bool:
        return self.task_type in PARENT_TYPES

    def matches(self, text: str) -> bool:
        haystack = fold(" ".join((self.title, self.notes, *self.tags)))
        return all(word in haystack for word in fold(text).split())

    @classmethod
    def from_dict(cls, record: dict[str, Any]) -> "Task":
        presentation = record.get("presentation") or {}
        parent = record.get("parent")
        completed = bool(record.get("completed"))
        return cls(
            task_id=record["task_id"],
            title=record.get("title") or "",
            task_type=record.get("task_type") or "normal",
            list_title=record.get("list_title") or "",
            notes=record.get("notes") or "",
            tags=tuple(tag.get("title", "") for tag in record.get("tags") or ()),
            tag_ids=tuple(tag.get("tag_id", "") for tag in record.get("tags") or ()),
            due=presentation.get("due_date_formatted") or record.get("due_date") or "",
            start=presentation.get("start_date_formatted")
            or record.get("start_date")
            or "",
            completed=completed,
            starred=bool(record.get("starred")),
            overdue=bool(presentation.get("is_overdue")) and not completed,
            child_count=len(record.get("child_task_ids") or ()),
            parent=Parent(parent["task_id"], parent["title"], parent["task_type"])
            if parent
            else None,
        )


@dataclass(frozen=True)
class Collection:
    kind: str
    entity: str
    title: str

    @classmethod
    def from_list(cls, record: dict[str, Any]) -> "Collection":
        return cls("list", record["list_id"], record.get("title") or "")

    @classmethod
    def from_smart_list(cls, record: dict[str, Any]) -> "Collection":
        return cls("smart", record["smart_list_id"], record.get("title") or "")


@dataclass(frozen=True)
class Tag:
    tag_id: str
    title: str
    paused: bool = False

    @classmethod
    def from_dict(cls, record: dict[str, Any]) -> "Tag":
        return cls(
            record["tag_id"], record.get("title") or "", bool(record.get("paused"))
        )
