from datetime import datetime, timezone
from threading import Lock

from app.models import Task, TaskCreate, TaskUpdate


class TaskStore:
    """In-memory task storage. Data is lost when the server restarts."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1
        self._lock = Lock()

    def create(self, data: TaskCreate) -> Task:
        with self._lock:
            task = Task(
                id=self._next_id,
                created_at=datetime.now(timezone.utc),
                **data.model_dump(),
            )
            self._tasks[task.id] = task
            self._next_id += 1
            return task

    def get(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def list(self) -> list[Task]:
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update(self, task_id: int, data: TaskUpdate) -> Task | None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            # title is required on Task, so an explicit null is ignored
            updates = {
                k: v
                for k, v in data.model_dump(exclude_unset=True).items()
                if k != "title" or v is not None
            }
            updated = task.model_copy(update=updates)
            self._tasks[task_id] = updated
            return updated

    def delete(self, task_id: int) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None

    def clear_done(self) -> int:
        removed = 0
        for task_id, task in self._tasks.items():
            if task.status == "done":
                del self._tasks[task_id]
                removed += 1
        return removed

    def clear(self) -> None:
        with self._lock:
            self._tasks.clear()
            self._next_id = 1


store = TaskStore()
