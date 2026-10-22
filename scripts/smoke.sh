#!/usr/bin/env bash
# Smoke tests against a running Task Tracker. Prints SMOKE OK and exits 0 only when every check passes.
# Usage: bash scripts/smoke.sh <base_url> <expected_version>
#   e.g. bash scripts/smoke.sh http://127.0.0.1:8001 0.3.0
# Creates one task and deletes it again, so it leaves the store as it found it.
set -uo pipefail

BASE="${1:?usage: smoke.sh <base_url> <expected_version>}"
EXPECTED_VERSION="${2:?usage: smoke.sh <base_url> <expected_version>}"
failures=0

fail() { echo "FAIL: $1"; failures=$((failures + 1)); }
# req METHOD PATH [JSON_BODY] -> sets $code and $body
req() {
  local out
  out="$(curl -s -w $'\n%{http_code}' -X "$1" -H 'Content-Type: application/json' ${3:+-d "$3"} "$BASE$2")" \
    || { code=000; body=""; return; }
  code="${out##*$'\n'}"; body="${out%$'\n'*}"
}
json() { python3 -c "import json,sys; print(json.loads(sys.argv[1])$1)" "$body" 2>/dev/null; }

# Wait up to 10s for a server that was just started.
for _ in $(seq 1 20); do req GET /health; [ "$code" = 200 ] && break; sleep 0.5; done
[ "$code" = 200 ] || { fail "GET /health returned $code (is the server running at $BASE?)"; echo "SMOKE FAILED"; exit 1; }

req GET /version
[ "$(json '["version"]')" = "$EXPECTED_VERSION" ] || fail "GET /version returned '$body', expected version $EXPECTED_VERSION"

title="smoke-$(date +%s)-$$"
req POST /tasks "{\"title\": \"$title\"}"
[ "$code" = 201 ] || fail "POST /tasks returned $code: $body"
id="$(json '["id"]')"

if [ -n "$id" ]; then
  req GET "/tasks/$id"
  [ "$code" = 200 ] && [ "$(json '["title"]')" = "$title" ] || fail "GET /tasks/$id returned $code: $body"

  req GET "/tasks?q=$title"
  [ "$code" = 200 ] && [ "$(json '["total"]')" = 1 ] || fail "GET /tasks?q=$title did not find exactly the new task ($code: $body)"

  req DELETE "/tasks/$id"
  [ "$code" = 204 ] || fail "DELETE /tasks/$id returned $code"

  req GET "/tasks/$id"
  [ "$code" = 404 ] || fail "GET /tasks/$id after delete returned $code, expected 404"
fi

if [ "$failures" -gt 0 ]; then
  echo "SMOKE FAILED ($failures issue(s))"
  exit 1
fi
echo "SMOKE OK ($BASE, version $EXPECTED_VERSION)"
