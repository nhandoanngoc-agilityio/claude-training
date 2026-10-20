from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class Status(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    due_date: date | None = None
    status: Status = Status.todo


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    due_date: date | None = None
    status: Status | None = None


class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    due_date: date | None = None
    status: Status = Status.todo
    created_at: datetime


class TaskPage(BaseModel):
    items: list[Task]
    page: int
    size: int
    total: int
    total_pages: int
