from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class DocumentData(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Sender's first name")
    middle_name: Optional[str] = Field(None, max_length=100, description="Sender's middle name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Sender's last name")
    date_created: str = Field(..., description="Date document was processed")
    doc_number: str = Field(..., min_length=1, max_length=50, description="DOC/Inmate ID number")
    facility_name: str = Field(..., min_length=1, max_length=200, description="Facility name")
    address: str = Field(..., min_length=1, max_length=500, description="Facility address")
    unit: Optional[str] = Field(None, max_length=50, description="Unit number")
    ai_summary: str = Field(..., min_length=1, description="AI-generated summary of the letter")
    raw_text: str = Field(..., min_length=1, description="Full OCR extracted text")
    
    @validator('date_created', pre=True, always=True)
    def set_date_created(cls, v):
        """Set current date if not provided."""
        if v is None or v == '':
            return datetime.now().strftime('%Y-%m-%d')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "middle_name": "A",
                "last_name": "Doe",
                "date_created": "2024-11-11",
                "doc_number": "123456",
                "facility_name": "California State Prison",
                "address": "123 Prison Rd, Sacramento, CA 95814",
                "unit": "B-Wing",
                "ai_summary": "Request for legal assistance regarding appeal case.",
                "raw_text": "Dear Family, I am writing to request..."
            }
        }


class FileProcessResult(BaseModel):
    filename: str = Field(..., description="Original filename")
    success: bool = Field(..., description="Whether processing was successful")
    data: Optional[DocumentData] = Field(None, description="Extracted data if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")


class ProcessResponse(BaseModel):
    total_files: int = Field(..., description="Total number of files submitted")
    processed: int = Field(..., description="Number of successfully processed files")
    failed: int = Field(..., description="Number of failed files")
    results: list[FileProcessResult] = Field(..., description="Individual file processing results")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")