from todolib.router import Route, parse

LIST = "list:aa11"
TASK = "task:bb22"


def test_empty_browse_query_is_the_menu() -> None:
    assert parse("") == Route("menu")


def test_unknown_words_filter_the_menu() -> None:
    assert parse("inb") == Route("menu", "inb", path="inb")


def test_focus_word_opens_the_focus_with_a_filter() -> None:
    assert parse("today dentist") == Route("focus", "dentist", "today", "today dentist")


def test_focus_words_are_case_insensitive() -> None:
    assert parse("Starred").entity == "starred"


def test_list_ref_opens_the_list() -> None:
    assert parse(f"> {LIST} milk") == Route("list", "milk", "aa11", f"> {LIST}", "")


def test_task_ref_inside_a_list_keeps_the_list_as_parent() -> None:
    assert parse(f"> {LIST} > {TASK} ") == Route(
        "task", "", "bb22", f"> {LIST} > {TASK}", f"> {LIST}"
    )


def test_task_ref_inside_a_focus_goes_back_to_the_focus() -> None:
    assert parse(f"today > {TASK}") == Route(
        "task", "", "bb22", f"today > {TASK}", "today"
    )


def test_marker_without_a_ref_is_ignored() -> None:
    assert parse("today >") == Route("focus", "", "today", "today")


def test_unknown_ref_is_ignored() -> None:
    assert parse("> nope:1").kind == "menu"


def test_ref_without_an_id_is_ignored() -> None:
    assert parse("> list:").kind == "menu"


def test_search_mode_searches_every_word() -> None:
    assert parse("today milk", "search") == Route(
        "search", "today milk", path="today milk"
    )


def test_search_mode_drills_into_a_parent() -> None:
    assert parse(f"milk > {TASK} oat", "search") == Route(
        "task", "oat", "bb22", f"milk > {TASK}", "milk"
    )


def test_done_mode_filters_done() -> None:
    assert parse("", "done") == Route("focus", "", "done", "")


def test_tags_word_opens_the_tags_page() -> None:
    assert parse("tags home") == Route("tags", "home", path="tags home")


def test_tag_ref_opens_the_tag() -> None:
    assert parse("tags > tag:g1 milk") == Route(
        "tag", "milk", "g1", "tags > tag:g1", "tags"
    )
