import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REFRESH_CLAIM_SECONDS = 120
PRIVATE_FILE = 0o600
PRIVATE_DIRECTORY = 0o700


@dataclass(frozen=True)
class CacheHit:
    data: Any
    stale: bool


class Cache:
    def __init__(self, directory: Path, clock: Callable[[], float]) -> None:
        self._directory = directory
        self._clock = clock

    def read(self, key: str, max_age_seconds: int) -> CacheHit | None:
        stored = self._load(self._path(key, "json"))
        if stored is None:
            return None
        age = self._clock() - stored["written_at"]
        return CacheHit(stored["data"], age > max_age_seconds)

    def write(self, key: str, data: object) -> None:
        stored = {"written_at": self._clock(), "data": data}
        self._write_private(self._path(key, "json"), json.dumps(stored))

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
        self._write_private(self._path(key, "lock"), str(self._clock()))
        return True

    def release_refresh(self, key: str) -> None:
        self._path(key, "lock").unlink(missing_ok=True)

    def _write_private(self, path: Path, text: str) -> None:
        self._directory.mkdir(mode=PRIVATE_DIRECTORY, parents=True, exist_ok=True)
        self._directory.chmod(PRIVATE_DIRECTORY)
        partial = path.with_suffix(path.suffix + ".partial")
        descriptor = os.open(
            partial, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, PRIVATE_FILE
        )
        with os.fdopen(descriptor, "w") as handle:
            handle.write(text)
        partial.chmod(PRIVATE_FILE)
        partial.replace(path)

    def _load(self, path: Path) -> dict[str, Any] | None:
        try:
            return json.loads(path.read_text())
        except (FileNotFoundError, ValueError):
            return None

    def _path(self, key: str, suffix: str) -> Path:
        return self._directory / f"{key}.{suffix}"
