from todolib.cache import REFRESH_CLAIM_SECONDS, Cache


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_missing_key_is_none(tmp_path):
    assert Cache(tmp_path, Clock()).read("x", 60) is None


def test_written_data_is_fresh_then_stale(tmp_path):
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


def test_corrupt_file_is_none(tmp_path):
    (tmp_path / "x.json").write_text("{")
    assert Cache(tmp_path, Clock()).read("x", 60) is None


def test_delete_removes_data(tmp_path):
    cache = Cache(tmp_path, Clock())
    cache.write("x", 1)
    cache.delete("x")
    assert cache.read("x", 60) is None


def test_claim_blocks_until_released_or_expired(tmp_path):
    clock = Clock()
    cache = Cache(tmp_path, clock)
    assert cache.claim_refresh("x")
    assert not cache.claim_refresh("x")
    cache.release_refresh("x")
    assert cache.claim_refresh("x")
    clock.now += REFRESH_CLAIM_SECONDS + 1
    assert cache.claim_refresh("x")
