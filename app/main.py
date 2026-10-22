from fastapi import FastAPI

from app.routers import tasks

app = FastAPI(title="Task Tracker", version="0.3.0", description="Practice API for the Claude Code training")
app.include_router(tasks.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": app.version}
