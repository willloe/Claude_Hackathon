"""
Q&A routes for student questions.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user
from ..services.rag_service import answer_question

router = APIRouter(prefix="/api/courses", tags=["qa"])


@router.post("/{course_id}/ask", response_model=schemas.AnswerResponse)
async def ask_question(
    course_id: UUID,
    question_data: schemas.QuestionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ask a question about the course materials.

    Args:
        course_id: Course ID
        question_data: Question to ask
        current_user: Current authenticated user
        db: Database session

    Returns:
        Answer with citations

    Raises:
        HTTPException: If course not found or not accessible
    """
    # Check course exists
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check access (students: only published, instructors: own courses)
    if current_user.role == models.UserRole.STUDENT:
        if not course.is_published:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Course not published"
            )
    else:  # Instructor
        if course.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    # Get course policy
    policy = db.query(models.CoursePolicy).filter(
        models.CoursePolicy.course_id == course_id
    ).first()

    # Answer the question using RAG
    try:
        result = await answer_question(
            course_id=str(course_id),
            question=question_data.question,
            course_name=course.name,
            term=course.term,
            policy=policy
        )

        # Log the Q&A
        qa_log = models.QALog(
            course_id=course_id,
            user_id=current_user.id,
            question_text=question_data.question,
            answer_text=result["answer"],
            sources=result["sources"],
            was_refused=result["was_refused"]
        )
        db.add(qa_log)
        db.commit()

        # Convert sources to schema
        source_objects = [
            schemas.SourceReference(**src) for src in result["sources"]
        ]

        return schemas.AnswerResponse(
            answer=result["answer"],
            sources=source_objects,
            was_refused=result["was_refused"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )
