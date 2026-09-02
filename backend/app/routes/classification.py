from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas import ClassifyRequest, ClassifyResponse, ResultsResponse, ClassificationRecord
from app.services.classification import classification_service
from app.database import Classification as ClassificationModel
from app.rate_limiter import limiter

router = APIRouter(prefix="/api", tags=["classification"])


@router.post("/classify", response_model=ClassifyResponse)
@limiter.limit("10/minute")
async def classify_text(request: Request, classify_request: ClassifyRequest, db: Session = Depends(get_db)):
    """
    Classify Roman Urdu text sentiment.
    Returns label (positive/negative/neutral) and confidence score.
    """
    label, confidence, raw_output = await classification_service.classify(classify_request.text)
    
    # Store in database
    classification = ClassificationModel(
        text=classify_request.text,
        label=label,
        confidence=confidence
    )
    db.add(classification)
    db.commit()
    db.refresh(classification)
    
    return ClassifyResponse(
        label=label,
        confidence=confidence,
        raw_output=raw_output
    )


@router.get("/results", response_model=ResultsResponse)
async def get_results(
    label: Optional[str] = Query(None, description="Filter by label: positive, negative, neutral"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """
    Get stored classifications with optional label filter.
    """
    query = db.query(ClassificationModel)
    
    if label:
        if label not in ["positive", "negative", "neutral", "unclassifiable"]:
            raise HTTPException(status_code=400, detail="Invalid label filter")
        query = query.filter(ClassificationModel.label == label)
    
    total = query.count()
    results = query.order_by(ClassificationModel.created_at.desc()).offset(offset).limit(limit).all()
    
    return ResultsResponse(
        results=[ClassificationRecord.model_validate(r) for r in results],
        total=total
    )