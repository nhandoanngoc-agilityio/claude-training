import unicodedata
from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status

from app.models import (
    OverdueTask,
    SortKey,
    SortOrder,
    Status,
    Task,
    TaskCreate,
    TaskPage,
    TaskUpdate,
)
from app.store import store

router = APIRouter(prefix="/tasks", tags=["tasks"])

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


def search_key(text: str) -> str:
    # canonical caseless form (Unicode D145), recomposed to NFC so "ba" doesn't match "bá"
    return unicodedata.normalize("NFC", unicodedata.normalize("NFD", text).casefold())


def sort_tasks(tasks: list[Task], key: SortKey, order: SortOrder) -> list[Task]:
    # ties keep id order in both directions: sort is stable, and reverse=True keeps it stable
    tasks = sorted(tasks, key=lambda t: t.id)
    reverse = order == SortOrder.desc
    if key == SortKey.due_date:
        # undated tasks go last whatever the order
        dated = [t for t in tasks if t.due_date is not None]
        undated = [t for t in tasks if t.due_date is None]
        return sorted(dated, key=lambda t: t.due_date, reverse=reverse) + undated
    if key == SortKey.title:
        return sorted(tasks, key=lambda t: t.title.casefold(), reverse=reverse)
    return sorted(tasks, key=lambda t: t.created_at, reverse=reverse)


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate) -> Task:
    return store.create(data)


@router.get("", response_model=TaskPage)
def list_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    status_filter: Status | None = Query(None, alias="status"),
    due_before: date | None = None,
    q: str | None = Query(None, min_length=1, max_length=200, pattern=r"\S"),
    sort: SortKey | None = None,
    order: SortOrder = SortOrder.asc,
) -> TaskPage:
    tasks = store.list()
    if q is not None:
        needle = search_key(q)
        tasks = [
            task
            for task in tasks
            if needle in search_key(task.title) or needle in search_key(task.description or "")
        ]
    if status_filter is not None:
        tasks = [task for task in tasks if task.status == status_filter]
    if due_before is not None:
        tasks = [task for task in tasks if task.due_date is not None and task.due_date < due_before]
    if sort is not None:
        tasks = sort_tasks(tasks, sort, order)

    total = len(tasks)
    total_pages = -(-total // size)  # round up without floats
    offset = (page - 1) * size
    return TaskPage(
        items=tasks[offset : offset + size],
        page=page,
        size=size,
        total=total,
        total_pages=total_pages,
    )


def utc_today() -> date:
    return datetime.now(timezone.utc).date()


@router.get("/overdue", response_model=list[OverdueTask])
def list_overdue_tasks() -> list[OverdueTask]:
    # strict like due_before: a task due today is not late yet
    today = utc_today()
    overdue = [
        OverdueTask(**task.model_dump(), days_late=(today - task.due_date).days)
        for task in store.list()
        if task.status != Status.done and task.due_date is not None and task.due_date < today
    ]
    return sorted(overdue, key=lambda t: (-t.days_late, t.id))


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
