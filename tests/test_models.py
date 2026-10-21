from tests.fakes import task_record
from todolib.models import Task, fold


def test_fold_ignores_case_and_accents() -> None:
    assert fold("Crème BRÛLÉE") == "creme brulee"


def test_task_reads_the_formatted_due_date() -> None:
    task = Task.from_dict(
        task_record(
            "t1",
            "Milk",
            due_date="2026-10-21",
            presentation={"due_date_formatted": "Today"},
        )
    )
    assert task.due == "Today"


def test_completed_task_is_never_overdue() -> None:
    task = Task.from_dict(
        task_record("t1", "Milk", completed=True, presentation={"is_overdue": True})
    )
    assert not task.overdue


def test_task_matches_title_notes_and_tags() -> None:
    task = Task.from_dict(
        task_record("t1", "Café run", notes="oat milk", tags=[{"title": "errand"}])
    )
    assert task.matches("cafe")
    assert task.matches("OAT errand")
    assert not task.matches("tea")


def test_checklist_is_a_parent() -> None:
    task = Task.from_dict(task_record("t1", "Pack", task_type="checklist"))
    assert task.is_parent


def test_task_reads_the_formatted_start_date() -> None:
    task = Task.from_dict(
        task_record(
            "t1",
            "Milk",
            start_date="2026-10-22",
            presentation={"start_date_formatted": "Tomorrow"},
        )
    )
    assert task.start == "Tomorrow"
