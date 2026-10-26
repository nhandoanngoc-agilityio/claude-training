# Security rules for this repo

Task Tracker is a training FastAPI app with in-memory storage and no auth. Focus findings on what can go wrong here:

- Request input (`title`, `description`, `q`, query params) must be limited in size by the models or `Query(...)`. Flag new inputs with no limit (unbounded work per request).
- No request input may reach `subprocess`, `os.system`, `eval`/`exec`, a file path, or a compiled regex.
- `TaskStore` writes must hold `self._lock`; flag read-then-write sequences outside the lock (race conditions).
- Error responses must not include stack traces, internal paths or environment values.
- Hooks in `.claude/hooks/` read JSON from stdin and inspect shell commands: flag anything that executes or `eval`s part of the command it is checking.
- Workflows in `.github/workflows/`: flag wider `permissions`, secrets exposed to `pull_request_target`, or untrusted PR text interpolated into `run:` steps.

Not findings here: missing authentication or authorization (no users by design), missing HTTPS, CORS, rate limiting, data persistence.
