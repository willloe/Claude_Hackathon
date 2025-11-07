"""
Course material management routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import os
import shutil
from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_instructor
from ..config import settings
from ..services.pdf_processor import process_pdf
from ..services.vector_store import vector_store

router = APIRouter(tags=["materials"])


@router.post("/api/courses/{course_id}/materials", response_model=schemas.MaterialResponse, status_code=status.HTTP_201_CREATED)
async def upload_material(
    course_id: UUID,
    file: UploadFile = File(...),
    file_type: models.MaterialType = Form(...),
    current_user: models.User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Upload a course material (PDF) and process it for RAG.

    Args:
        course_id: Course ID
        file: Uploaded PDF file
        file_type: Type of material
        current_user: Current authenticated instructor
        db: Database session

    Returns:
        Created material information

    Raises:
        HTTPException: If course not found, access denied, or file invalid
    """
    # Check course exists and user owns it
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

    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)

    # Save file
    file_path = os.path.join(settings.UPLOADS_DIR, f"{course_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create material record
    material = models.CourseMaterial(
        course_id=course_id,
        filename=file.filename,
        file_type=file_type,
        storage_path=file_path,
        processed=False
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    # Process PDF asynchronously (or synchronously for demo)
    try:
        chunks = process_pdf(file_path, str(course_id), str(material.id), file.filename)

        # Store in vector database
        vector_store.add_documents(chunks, str(course_id))

        # Update material as processed
        material.processed = True
        material.chunk_count = len(chunks)
        db.commit()
        db.refresh(material)
    except Exception as e:
        # If processing fails, mark as not processed but keep the record
        print(f"Error processing PDF: {e}")
        # Don't raise error, just mark as not processed

    return schemas.MaterialResponse.from_orm(material)


@router.get("/api/courses/{course_id}/materials", response_model=List[schemas.MaterialResponse])
def list_materials(
    course_id: UUID,
    current_user: models.User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    List all materials for a course (instructor only).

    Args:
        course_id: Course ID
        current_user: Current authenticated instructor
        db: Database session

    Returns:
        List of materials

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

    materials = db.query(models.CourseMaterial).filter(
        models.CourseMaterial.course_id == course_id
    ).all()

    return [schemas.MaterialResponse.from_orm(m) for m in materials]


@router.delete("/api/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: UUID,
    current_user: models.User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Delete a course material (instructor only).

    Args:
        material_id: Material ID
        current_user: Current authenticated instructor
        db: Database session

    Raises:
        HTTPException: If material not found or access denied
    """
    material = db.query(models.CourseMaterial).filter(
        models.CourseMaterial.id == material_id
    ).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )

    # Check ownership through course
    course = db.query(models.Course).filter(models.Course.id == material.course_id).first()
    if course.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Delete file from storage
    if os.path.exists(material.storage_path):
        os.remove(material.storage_path)

    # Delete from vector store
    # Note: ChromaDB doesn't have easy per-document deletion,
    # so we'll just delete the DB record for now
    db.delete(material)
    db.commit()

    return None


@router.put("/api/courses/{course_id}/policies", response_model=schemas.PolicyResponse)
def update_policies(
    course_id: UUID,
    policy_data: schemas.PolicyCreate,
    current_user: models.User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Set or update course policies (instructor only).

    Args:
        course_id: Course ID
        policy_data: Policy configuration
        current_user: Current authenticated instructor
        db: Database session

    Returns:
        Updated policy information

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

    # Check if policy exists
    policy = db.query(models.CoursePolicy).filter(
        models.CoursePolicy.course_id == course_id
    ).first()

    if policy:
        # Update existing policy
        for field, value in policy_data.dict().items():
            setattr(policy, field, value)
    else:
        # Create new policy
        policy = models.CoursePolicy(
            course_id=course_id,
            **policy_data.dict()
        )
        db.add(policy)

    db.commit()
    db.refresh(policy)

    return schemas.PolicyResponse.from_orm(policy)


@router.get("/api/courses/{course_id}/policies", response_model=schemas.PolicyResponse)
def get_policies(
    course_id: UUID,
    current_user: models.User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Get course policies (instructor only).

    Args:
        course_id: Course ID
        current_user: Current authenticated instructor
        db: Database session

    Returns:
        Policy information

    Raises:
        HTTPException: If course or policy not found, or access denied
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

    policy = db.query(models.CoursePolicy).filter(
        models.CoursePolicy.course_id == course_id
    ).first()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not configured"
        )

    return schemas.PolicyResponse.from_orm(policy)
