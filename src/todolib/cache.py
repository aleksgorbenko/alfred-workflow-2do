import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REFRESH_CLAIM_SECONDS = 120


@dataclass(frozen=True)
class CacheHit:
    data: Any
    stale: bool


class Cache:
    def __init__(self, directory: Path, clock: Callable[[], float]):
        self._directory = directory
        self._clock = clock

    def read(self, key: str, max_age_seconds: int) -> CacheHit | None:
        stored = self._load(self._path(key, "json"))
        if stored is None:
            return None
        age = self._clock() - stored["written_at"]
        return CacheHit(stored["data"], age > max_age_seconds)

    def write(self, key: str, data: Any) -> None:
        self._directory.mkdir(parents=True, exist_ok=True)
        stored = {"written_at": self._clock(), "data": data}
        self._path(key, "json").write_text(json.dumps(stored))

    def delete(self, key: str) -> None:
        self._path(key, "json").unlink(missing_ok=True)

    def claim_refresh(self, key: str) -> bool:
        try:
            claimed_at = float(self._path(key, "lock").read_text())
        except (FileNotFoundError, ValueError):
            claimed_at = None
        if (
            claimed_at is not None
            and self._clock() - claimed_at < REFRESH_CLAIM_SECONDS
        ):
            return False
        self._directory.mkdir(parents=True, exist_ok=True)
        self._path(key, "lock").write_text(str(self._clock()))
        return True

    def release_refresh(self, key: str) -> None:
        self._path(key, "lock").unlink(missing_ok=True)

    def _load(self, path: Path) -> dict[str, Any] | None:
        try:
            return json.loads(path.read_text())
        except (FileNotFoundError, ValueError):
            return None

    def _path(self, key: str, suffix: str) -> Path:
        return self._directory / f"{key}.{suffix}"
