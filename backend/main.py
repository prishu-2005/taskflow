from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from algorithms import binary_search_tasks, merge_sort_tasks
from sqlalchemy import func
import time

from database import Base, engine, get_db
import models
import schemas


app = FastAPI(title="TaskFlow API")


# Create database tables
Base.metadata.create_all(bind=engine)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)


# Request timing middleware
@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = (time.perf_counter() - start_time) * 1000

    print(
        f"{request.method} {request.url.path} - "
        f"{process_time:.2f} ms"
    )

    return response


# Root
@app.get("/")
def root():
    return {"message": "TaskFlow API is running"}


# ---------------- USERS ----------------

@app.post("/users", response_model=schemas.UserResponse)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    new_user = models.User(
        name=user.name,
        email=user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


# ---------------- PROJECTS ----------------

@app.post("/projects", response_model=schemas.ProjectResponse)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db)
):
    new_project = models.Project(
        name=project.name,
        owner_id=project.owner_id
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@app.get("/projects", response_model=list[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()


# ---------------- TASKS ----------------

@app.post("/tasks", response_model=schemas.TaskResponse)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db)
):
    new_task = models.Task(
        title=task.title,
        priority=task.priority,
        due_date=task.due_date,
        status=task.status,
        project_id=task.project_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@app.get("/tasks", response_model=list[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()


@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task: schemas.TaskCreate,
    db: Session = Depends(get_db)
):
    existing_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if existing_task is None:
        return {"detail": "Task not found"}

    existing_task.title = task.title
    existing_task.priority = task.priority
    existing_task.due_date = task.due_date
    existing_task.status = task.status
    existing_task.project_id = task.project_id

    db.commit()
    db.refresh(existing_task)

    return existing_task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    existing_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if existing_task is None:
        return {"detail": "Task not found"}

    db.delete(existing_task)
    db.commit()

    return {"message": "Task deleted successfully"}


# ---------------- STATISTICS ----------------

@app.get("/projects/statistics")
def project_statistics(db: Session = Depends(get_db)):
    results = (
        db.query(
            models.Project.id.label("project_id"),
            models.Project.name.label("project_name"),
            func.count(models.Task.id).label("task_count")
        )
        .outerjoin(
            models.Task,
            models.Project.id == models.Task.project_id
        )
        .group_by(
            models.Project.id,
            models.Project.name
        )
        .all()
    )

    return [
        {
            "project_id": row.project_id,
            "project_name": row.project_name,
            "task_count": row.task_count
        }
        for row in results
    ]


@app.get("/tasks/search", response_model=schemas.TaskResponse | None)
def search_task(
    title: str,
    db: Session = Depends(get_db)
):
    tasks = (
        db.query(models.Task)
        .order_by(models.Task.title)
        .all()
    )

    result = binary_search_tasks(tasks, title)

    return result

@app.get("/tasks/sorted", response_model=list[schemas.TaskResponse])
def get_sorted_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()

    sorted_tasks = merge_sort_tasks(tasks)

    return sorted_tasks

