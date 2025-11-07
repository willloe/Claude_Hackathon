"""
Analytics routes for instructors.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import List
from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_instructor

router = APIRouter(prefix="/api/courses", tags=["analytics"])


@router.get("/{course_id}/qa-logs", response_model=List[schemas.QALogResponse])
def get_qa_logs(
    course_id: UUID,
    limit: int = 50,
    current_user: models.User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Get Q&A history for a course (instructor only).

    Args:
        course_id: Course ID
        limit: Maximum number of logs to return
        current_user: Current authenticated instructor
        db: Database session

    Returns:
        List of Q&A logs

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

    logs = db.query(models.QALog).filter(
        models.QALog.course_id == course_id
    ).order_by(models.QALog.created_at.desc()).limit(limit).all()

    return [schemas.QALogResponse.from_orm(log) for log in logs]


@router.get("/{course_id}/analytics", response_model=schemas.AnalyticsResponse)
def get_analytics(
    course_id: UUID,
    current_user: models.User = Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """
    Get course analytics (instructor only).

    Args:
        course_id: Course ID
        current_user: Current authenticated instructor
        db: Database session

    Returns:
        Course analytics

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

    # Get total questions
    total_questions = db.query(func.count(models.QALog.id)).filter(
        models.QALog.course_id == course_id
    ).scalar() or 0

    # Get refusal count
    refusal_count = db.query(func.count(models.QALog.id)).filter(
        models.QALog.course_id == course_id,
        models.QALog.was_refused == True
    ).scalar() or 0

    # Calculate refusal rate
    refusal_rate = (refusal_count / total_questions * 100) if total_questions > 0 else 0.0

    # Get recent questions
    recent_questions = db.query(models.QALog).filter(
        models.QALog.course_id == course_id
    ).order_by(models.QALog.created_at.desc()).limit(10).all()

    # Extract top topics (simple keyword extraction from questions)
    all_logs = db.query(models.QALog).filter(
        models.QALog.course_id == course_id
    ).all()

    # Simple topic extraction: get common words from questions
    from collections import Counter
    words = []
    for log in all_logs:
        # Simple word extraction (in production, use NLP)
        question_words = log.question_text.lower().split()
        words.extend([w for w in question_words if len(w) > 4])

    word_counts = Counter(words)
    top_topics = [word for word, count in word_counts.most_common(5)]

    return schemas.AnalyticsResponse(
        total_questions=total_questions,
        refusal_count=refusal_count,
        refusal_rate=round(refusal_rate, 2),
        recent_questions=[schemas.QALogResponse.from_orm(q) for q in recent_questions],
        top_topics=top_topics
    )
