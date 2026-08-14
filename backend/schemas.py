from pydantic import BaseModel, Field, field_validator
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    owner_id: int


class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    priority: str = Field(
        default="medium",
        pattern="^(low|medium|high)$"
    )
    due_date: Optional[str] = None
    status: str = "todo"
    project_id: int

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value):
        if not value.strip():
            raise ValueError("Title cannot be blank")
        return value.strip()

class QuickAddRequest(BaseModel):
    description: str
    project_id: int

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, value):
        if not value.strip():
            raise ValueError("Description cannot be blank")
        return value


class TaskResponse(BaseModel):
    id: int
    title: str
    priority: str
    due_date: Optional[str]
    status: str
    project_id: int

    class Config:
        from_attributes = True