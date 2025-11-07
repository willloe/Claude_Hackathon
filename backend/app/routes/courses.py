"""
Course management routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user, get_current_instructor

router = APIRouter(prefix="/api/courses", tags=["courses"])


@router.post("", response_model=schemas.CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: schemas.CourseCreate,
    current_user: models.User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Create a new course (instructor only).

    Args:
        course_data: Course creation data
        current_user: Current authenticated instructor
        db: Database session

    Returns:
        Created course information
    """
    new_course = models.Course(
        name=course_data.name,
        term=course_data.term,
        owner_id=current_user.id,
        is_published=course_data.is_published,
        office_hours=course_data.office_hours,
        instructor_email=course_data.instructor_email,
        location=course_data.location,
        late_policy=course_data.late_policy
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return schemas.CourseResponse.from_orm(new_course)


@router.get("", response_model=List[schemas.CourseResponse])
def list_courses(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all courses.
    - Instructors see their own courses
    - Students see published courses

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of courses
    """
    if current_user.role == models.UserRole.INSTRUCTOR:
        # Instructors see their own courses
        courses = db.query(models.Course).filter(
            models.Course.owner_id == current_user.id
        ).all()
    else:
        # Students see published courses
        courses = db.query(models.Course).filter(
            models.Course.is_published == True
        ).all()

    return [schemas.CourseResponse.from_orm(course) for course in courses]


@router.get("/{course_id}", response_model=schemas.CourseResponse)
def get_course(
    course_id: UUID,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get course details.

    Args:
        course_id: Course ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Course information

    Raises:
        HTTPException: If course not found or access denied
    """
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check access: instructor owns it OR student and it's published
    if current_user.role == models.UserRole.INSTRUCTOR:
        if course.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:  # Student
        if not course.is_published:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Course not published"
            )

    return schemas.CourseResponse.from_orm(course)


@router.put("/{course_id}", response_model=schemas.CourseResponse)
def update_course(
    course_id: UUID,
    course_data: schemas.CourseUpdate,
    current_user: models.User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Update course details (instructor only, must own course).

    Args:
        course_id: Course ID
        course_data: Course update data
        current_user: Current authenticated instructor
        db: Database session

    Returns:
        Updated course information

    Raises:
        HTTPException: If course not found or access denied
    """
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    if course.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Update fields if provided
    update_data = course_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)

    return schemas.CourseResponse.from_orm(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: UUID,
    current_user: models.User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Delete a course (instructor only, must own course).

    Args:
        course_id: Course ID
        current_user: Current authenticated instructor
        db: Database session

    Raises:
        HTTPException: If course not found or access denied
    """
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    if course.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    db.delete(course)
    db.commit()

    return None
