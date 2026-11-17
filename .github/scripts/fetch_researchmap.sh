#!/usr/bin/env bash
set -euo pipefail

# Print validated API data. Exit 75 for a temporary outage so the caller can
# preserve the existing site; other errors must still fail the workflow.
response_file=$(mktemp)
trap 'rm -f "$response_file"' EXIT

for attempt in 1 2 3; do
  if http_status=$(curl --silent --show-error --location \
    --connect-timeout 10 --max-time 60 \
    --output "$response_file" --write-out '%{http_code}' "$1"); then
    case "$http_status" in
      2??)
        if ! jq -e -s 'length == 1 and (.[0].items | type == "array")' "$response_file" >/dev/null; then
          echo "ResearchMap returned invalid JSON or a missing items array: $1" >&2
          exit 1
        fi
        cat "$response_file"
        exit 0
        ;;
      429|5??)
        echo "ResearchMap temporarily unavailable (HTTP $http_status, attempt $attempt/3): $1" >&2
        ;;
      *)
        echo "ResearchMap request failed (HTTP $http_status): $1" >&2
        exit 1
        ;;
    esac
  else
    echo "ResearchMap connection failed (attempt $attempt/3): $1" >&2
  fi

  if [[ "$attempt" -lt 3 ]]; then
    sleep "$((attempt * 5))"
  fi
done

exit 75
