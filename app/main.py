from fastapi import FastAPI

from app.routers import tasks

app = FastAPI(title="Task Tracker", version="0.1.0")
app.include_router(tasks.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
