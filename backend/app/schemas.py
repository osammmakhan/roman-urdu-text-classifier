from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Roman Urdu text to classify")


class ClassifyResponse(BaseModel):
    label: str = Field(..., description="Classification label: positive, negative, or neutral")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    raw_output: Optional[str] = Field(None, description="Raw model output for debugging")


class ClassificationRecord(BaseModel):
    id: int
    text: str
    label: str
    confidence: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResultsResponse(BaseModel):
    results: list[ClassificationRecord]
    total: int