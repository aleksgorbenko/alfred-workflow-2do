#!/bin/bash
set -euo pipefail

export PATH="$HOME/.local/share/mise/shims:/opt/homebrew/bin:/usr/local/bin:$PATH"

remembered="${alfred_workflow_cache:?}/python"
setting="${python_path:-}"
setting="${setting/#\~/$HOME}"

resolve() {
  [[ -x "$1" ]] && "$1" -c 'import sys; print(sys.executable) if sys.version_info >= (3, 11) else sys.exit(1)' 2>/dev/null
}

if [[ -f "$remembered" ]]; then
  IFS='|' read -r remembered_setting remembered_python <"$remembered"
  if [[ "$remembered_setting" == "$setting" && -x "$remembered_python" ]]; then
    exec "$remembered_python" "$@"
  fi
fi

candidates=()
if [[ -n "$setting" ]]; then
  candidates+=("$setting")
fi
while IFS= read -r found; do
  candidates+=("$found")
done < <(type -aP python3 || true)

for candidate in ${candidates[@]+"${candidates[@]}"}; do
  if resolved="$(resolve "$candidate")" && [[ -x "$resolved" ]]; then
    mkdir -p "$alfred_workflow_cache"
    printf '%s|%s\n' "$setting" "$resolved" >"$remembered"
    exec "$resolved" "$@"
  fi
done

json_text() {
  local text="${1//\\/\\\\}"
  printf '"%s"' "${text//\"/\\\"}"
}

printf '{"items": [{"title": %s, "subtitle": %s, "valid": false, "icon": {"path": "icons/error.png"}}]}\n' \
  "$(json_text "${title_no_python:?}")" "$(json_text "${subtitle_no_python:?}")"
