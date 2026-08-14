from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import ValidationError
import time

from algorithms import binary_search_tasks, merge_sort_tasks
from database import Base, engine, get_db
import models
import schemas
from ai_parser import parse_task_description, parse_with_groq


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


# ---------------- ROOT ----------------

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


# ---------------- AI QUICK-ADD ----------------

@app.post(
    "/tasks/quick-add",
    response_model=schemas.TaskResponse,
    status_code=201
)
def quick_add_task(
    request: schemas.QuickAddRequest,
    db: Session = Depends(get_db)
):
    # 1. Check that the project exists BEFORE creating a task
    project = (
        db.query(models.Project)
        .filter(models.Project.id == request.project_id)
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=422,
            detail="Project does not exist"
        )

    # 2. Try optional Groq parser
    # If Groq is disabled or unavailable, use the required mock.
    parsed = None

    try:
        parsed = parse_with_groq(request.description)
    except Exception:
        parsed = None

    if parsed is None:
        parsed = parse_task_description(request.description)

    # 3. Convert parser result into the TaskResponse structure.
    task_data = {
        "id": 0,
        "title": parsed.get("title"),
        "priority": parsed.get("priority"),
        "due_date": parsed.get("due_date_hint"),
        "status": "todo",
        "project_id": request.project_id
    }

    # 4. Validate BEFORE touching the database.
    try:
        validated_task = schemas.TaskResponse.model_validate(task_data)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors()
        )

    # 5. Create the actual SQLAlchemy Task row.
    new_task = models.Task(
        title=validated_task.title,
        priority=validated_task.priority,
        due_date=validated_task.due_date,
        status=validated_task.status,
        project_id=validated_task.project_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# ---------------- GET SINGLE TASK ----------------

@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id)
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# ---------------- UPDATE TASK ----------------

@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task: schemas.TaskCreate,
    db: Session = Depends(get_db)
):
    existing_task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id)
        .first()
    )

    if existing_task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    existing_task.title = task.title
    existing_task.priority = task.priority
    existing_task.due_date = task.due_date
    existing_task.status = task.status
    existing_task.project_id = task.project_id

    db.commit()
    db.refresh(existing_task)

    return existing_task


# ---------------- DELETE TASK ----------------

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    existing_task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id)
        .first()
    )

    if existing_task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

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


# ---------------- SEARCH ----------------

@app.get(
    "/tasks/search",
    response_model=schemas.TaskResponse | None
)
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


# ---------------- SORTED TASKS ----------------

@app.get(
    "/tasks/sorted",
    response_model=list[schemas.TaskResponse]
)
def get_sorted_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()

    sorted_tasks = merge_sort_tasks(tasks)

    return sorted_tasks