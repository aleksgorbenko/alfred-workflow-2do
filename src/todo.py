import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT)]

from todolib.app import Deps, perform, refresh, run  # noqa: E402
from todolib.bridge import Bridge, run_osascript  # noqa: E402
from todolib.cache import Cache  # noqa: E402


def spawn_refresh() -> None:
    subprocess.Popen(
        [sys.executable, __file__, "--refresh"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def build_deps() -> Deps:
    cache_dir = Path(os.environ["alfred_workflow_cache"])  # noqa: SIM112
    return Deps(
        bridge=Bridge(run_osascript, ROOT / "bridge.js"),
        cache=Cache(cache_dir / "data", time.time),
        refresh=spawn_refresh,
    )


def main(argv: list[str]) -> None:
    deps = build_deps()
    command = argv[0] if argv else ""
    query = argv[1] if len(argv) > 1 else ""
    if command == "--refresh":
        refresh(deps)
    elif command == "--perform":
        perform(
            os.environ.get("action", ""),  # noqa: SIM112
            os.environ.get("target", ""),  # noqa: SIM112
            deps,
        )
    else:
        print(json.dumps(run(query, command.removeprefix("--") or "browse", deps)))


if __name__ == "__main__":
    main(sys.argv[1:])
