"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .models import UserRole, MaterialType, PersonaType


# ============= Auth Schemas =============
class UserCreate(BaseModel):
    """Schema for user registration."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    name: str
    email: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============= Course Schemas =============
class CourseCreate(BaseModel):
    """Schema for creating a course."""
    name: str = Field(..., min_length=1, max_length=255)
    term: str = Field(..., min_length=1, max_length=100)
    office_hours: Optional[str] = None
    instructor_email: Optional[EmailStr] = None
    location: Optional[str] = None
    late_policy: Optional[str] = None
    is_published: bool = False


class CourseUpdate(BaseModel):
    """Schema for updating a course."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    term: Optional[str] = Field(None, min_length=1, max_length=100)
    office_hours: Optional[str] = None
    instructor_email: Optional[EmailStr] = None
    location: Optional[str] = None
    late_policy: Optional[str] = None
    is_published: Optional[bool] = None


class CourseResponse(BaseModel):
    """Schema for course response."""
    id: UUID
    name: str
    term: str
    owner_id: UUID
    is_published: bool
    office_hours: Optional[str]
    instructor_email: Optional[str]
    location: Optional[str]
    late_policy: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Material Schemas =============
class MaterialResponse(BaseModel):
    """Schema for material response."""
    id: UUID
    course_id: UUID
    filename: str
    file_type: MaterialType
    storage_path: str
    processed: bool
    chunk_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Policy Schemas =============
class PolicyCreate(BaseModel):
    """Schema for creating/updating course policy."""
    persona: PersonaType = PersonaType.FRIENDLY
    allowed_topics: Optional[str] = None
    disallowed_actions: Optional[str] = None
    custom_instructions: Optional[str] = None


class PolicyResponse(BaseModel):
    """Schema for policy response."""
    id: UUID
    course_id: UUID
    persona: PersonaType
    allowed_topics: Optional[str]
    disallowed_actions: Optional[str]
    custom_instructions: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Q&A Schemas =============
class QuestionRequest(BaseModel):
    """Schema for asking a question."""
    question: str = Field(..., min_length=1)


class SourceReference(BaseModel):
    """Schema for a source reference in an answer."""
    filename: str
    page: int
    chunk_text: str


class AnswerResponse(BaseModel):
    """Schema for answer response."""
    answer: str
    sources: List[SourceReference]
    was_refused: bool


class QALogResponse(BaseModel):
    """Schema for Q&A log response."""
    id: UUID
    course_id: UUID
    user_id: Optional[UUID]
    question_text: str
    answer_text: str
    sources: Optional[List[dict]]
    was_refused: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Analytics Schemas =============
class AnalyticsResponse(BaseModel):
    """Schema for course analytics."""
    total_questions: int
    refusal_count: int
    refusal_rate: float
    recent_questions: List[QALogResponse]
    top_topics: List[str]
