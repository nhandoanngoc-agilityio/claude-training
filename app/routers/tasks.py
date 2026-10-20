from datetime import date

from fastapi import APIRouter, HTTPException, Query, status

from app.models import Status, Task, TaskCreate, TaskPage, TaskUpdate
from app.store import store

router = APIRouter(prefix="/tasks", tags=["tasks"])

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate) -> Task:
    return store.create(data)


@router.get("", response_model=TaskPage)
def list_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    status_filter: Status | None = Query(None, alias="status"),
    due_before: date | None = None,
) -> TaskPage:
    tasks = store.list()
    if status_filter is not None:
        tasks = [task for task in tasks if task.status == status_filter]
    if due_before is not None:
        tasks = [task for task in tasks if task.due_date is not None and task.due_date < due_before]

    total = len(tasks)
    total_pages = total // size
    offset = (page - 1) * size
    return TaskPage(
        items=tasks[offset : offset + size],
        page=page,
        size=size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=Task)
def update_task(task_id: int, data: TaskUpdate) -> Task:
    task = store.update(task_id, data)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    if not store.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
