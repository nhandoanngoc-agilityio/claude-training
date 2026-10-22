#!/usr/bin/env bash
# Release preflight checks. Prints PREFLIGHT OK and exits 0 only when every check passes.
# Override DEFAULT_BRANCH / REMOTE with env vars if your repo differs.
set -uo pipefail

REMOTE="${REMOTE:-origin}"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-$(git symbolic-ref --short "refs/remotes/$REMOTE/HEAD" 2>/dev/null | sed "s#^$REMOTE/##")}"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"
failures=0

fail() { echo "FAIL: $1"; echo "  fix: $2"; failures=$((failures + 1)); }

branch="$(git rev-parse --abbrev-ref HEAD)"
[ "$branch" = "$DEFAULT_BRANCH" ] || fail "on branch '$branch', expected '$DEFAULT_BRANCH'" "git switch $DEFAULT_BRANCH"

[ -z "$(git status --porcelain)" ] || fail "working tree has uncommitted changes" "commit or stash them (git status)"

git fetch --quiet "$REMOTE" "$DEFAULT_BRANCH" --tags
local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "$REMOTE/$DEFAULT_BRANCH")"
[ "$local_sha" = "$remote_sha" ] || fail "HEAD ($local_sha) differs from $REMOTE/$DEFAULT_BRANCH ($remote_sha)" "git pull --ff-only"

if command -v glab >/dev/null 2>&1; then
  ci="$(glab api "projects/:id/pipelines?sha=$remote_sha&ref=$DEFAULT_BRANCH" 2>/dev/null | python3 -c '
import json,sys
ps=json.load(sys.stdin)
if not ps: print("none")
elif ps[0]["status"]=="success": print("success")
elif ps[0]["status"] in ("created","pending","running","waiting_for_resource","preparing"): print("pending")
else: print("failure")')"
  case "$ci" in
    success) ;;
    pending) fail "CI is still running on $remote_sha" "wait for it to finish, then rerun preflight" ;;
    none)    fail "no CI pipelines found for $remote_sha" "check the GitLab pipeline was triggered" ;;
    *)       fail "CI is not green on $remote_sha" "glab ci list" ;;
  esac
else
  fail "glab CLI not installed, cannot check CI" "install glab or check CI manually and tell the user"
fi

if [ "$failures" -gt 0 ]; then
  echo "PREFLIGHT FAILED ($failures issue(s))"
  exit 1
fi
echo "PREFLIGHT OK (branch $DEFAULT_BRANCH @ ${remote_sha:0:8}, last tag: $(git describe --tags --abbrev=0 2>/dev/null || echo none))"
