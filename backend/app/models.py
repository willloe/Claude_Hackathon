"""
SQLAlchemy database models for the AI TA Platform.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from .database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    INSTRUCTOR = "instructor"
    STUDENT = "student"


class MaterialType(str, enum.Enum):
    """Course material type enumeration."""
    SYLLABUS = "syllabus"
    LECTURE = "lecture"
    ASSIGNMENT = "assignment"
    TRANSCRIPT = "transcript"


class PersonaType(str, enum.Enum):
    """AI TA persona type enumeration."""
    POLICY_FIRST = "policy_first"
    FRIENDLY = "friendly"
    SCAFFOLDED = "scaffolded"


class User(Base):
    """User model for instructors and students."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    courses = relationship("Course", back_populates="owner", cascade="all, delete-orphan")
    qa_logs = relationship("QALog", back_populates="user")


class Course(Base):
    """Course model."""
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    term = Column(String(100), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    office_hours = Column(String(255), nullable=True)
    instructor_email = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    late_policy = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="courses")
    materials = relationship("CourseMaterial", back_populates="course", cascade="all, delete-orphan")
    policy = relationship("CoursePolicy", back_populates="course", uselist=False, cascade="all, delete-orphan")
    qa_logs = relationship("QALog", back_populates="course", cascade="all, delete-orphan")


class CourseMaterial(Base):
    """Course material model for uploaded PDFs."""
    __tablename__ = "course_materials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(SQLEnum(MaterialType), nullable=False)
    storage_path = Column(String(512), nullable=False)
    processed = Column(Boolean, default=False, nullable=False)
    chunk_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="materials")


class CoursePolicy(Base):
    """Course policy and AI TA configuration."""
    __tablename__ = "course_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), unique=True, nullable=False)
    persona = Column(SQLEnum(PersonaType), default=PersonaType.FRIENDLY, nullable=False)
    allowed_topics = Column(Text, nullable=True)
    disallowed_actions = Column(Text, nullable=True)
    custom_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="policy")


class QALog(Base):
    """Q&A interaction log."""
    __tablename__ = "qa_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    sources = Column(JSONB, nullable=True)  # Array of {filename, page, chunk_text}
    was_refused = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="qa_logs")
    user = relationship("User", back_populates="qa_logs")
