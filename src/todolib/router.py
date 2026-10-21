from dataclasses import dataclass

MARKER = ">"
FOCUSES = ("today", "starred", "scheduled", "all", "done")
REFS = ("list", "smart", "task", "tag")
TAGS = "tags"


@dataclass(frozen=True)
class Route:
    kind: str
    text: str = ""
    entity: str = ""
    path: str = ""
    parent: str = ""


def _ref(word: str) -> tuple[str, str] | None:
    kind, _, entity = word.partition(":")
    if kind in REFS and entity:
        return kind, entity
    return None


def _start(mode: str, words: list[str]) -> Route:
    path = " ".join(words)
    if mode == "browse":
        if words and words[0].casefold() in FOCUSES:
            focus = words[0].casefold()
            return Route("focus", " ".join(words[1:]), focus, path)
        if words and words[0].casefold() == TAGS:
            return Route(TAGS, " ".join(words[1:]), path=path)
        return Route("menu", path, path=path)
    if mode in ("today", "done"):
        return Route("focus", path, mode, path)
    return Route("search", path, path=path)


def parse(query: str, mode: str = "browse") -> Route:
    words = query.split()
    refs = [
        index
        for index in range(len(words) - 1)
        if words[index] == MARKER and _ref(words[index + 1])
    ]
    if not refs:
        return _start(mode, [word for word in words if word != MARKER])
    path = _start(mode, words[: refs[0]]).path
    parent = path
    for index in refs:
        parent, path = path, f"{path} {MARKER} {words[index + 1]}".strip()
    last = refs[-1] + 1
    kind, entity = _ref(words[last]) or ("", "")
    text = " ".join(word for word in words[last + 1 :] if word != MARKER)
    return Route(kind, text, entity, path, parent)
