from pathlib import Path

from todolib.cache import (
    PRIVATE_DIRECTORY,
    PRIVATE_FILE,
    REFRESH_CLAIM_SECONDS,
    Cache,
)


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_missing_key_is_none(tmp_path: Path) -> None:
    assert Cache(tmp_path, Clock()).read("x", 60) is None


def test_written_data_is_fresh_then_stale(tmp_path: Path) -> None:
    clock = Clock()
    cache = Cache(tmp_path, clock)
    cache.write("x", [1])
    hit = cache.read("x", 60)
    assert hit is not None
    assert (hit.data, hit.stale) == ([1], False)
    clock.now += 61
    hit = cache.read("x", 60)
    assert hit is not None
    assert hit.stale


def test_corrupt_file_is_none(tmp_path: Path) -> None:
    (tmp_path / "x.json").write_text("{")
    assert Cache(tmp_path, Clock()).read("x", 60) is None


def test_delete_removes_data(tmp_path: Path) -> None:
    cache = Cache(tmp_path, Clock())
    cache.write("x", 1)
    cache.delete("x")
    assert cache.read("x", 60) is None


def test_claim_blocks_until_released_or_expired(tmp_path: Path) -> None:
    clock = Clock()
    cache = Cache(tmp_path, clock)
    assert cache.claim_refresh("x")
    assert not cache.claim_refresh("x")
    cache.release_refresh("x")
    assert cache.claim_refresh("x")
    clock.now += REFRESH_CLAIM_SECONDS + 1
    assert cache.claim_refresh("x")


def test_written_files_are_private(tmp_path: Path) -> None:
    directory = tmp_path / "data"
    directory.mkdir(mode=0o755)
    stale = directory / "x.json"
    stale.write_text("{}")
    stale.chmod(0o644)
    cache = Cache(directory, Clock())
    cache.write("x", [1])
    cache.claim_refresh("x")
    assert directory.stat().st_mode & 0o777 == PRIVATE_DIRECTORY
    assert stale.stat().st_mode & 0o777 == PRIVATE_FILE
    assert (directory / "x.lock").stat().st_mode & 0o777 == PRIVATE_FILE
