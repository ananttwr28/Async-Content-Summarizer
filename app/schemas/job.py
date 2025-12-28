from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class JobSubmitResponse(BaseModel):
    job_id: UUID
    status: str

class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    created_at: datetime

class JobResultResponse(BaseModel):
    job_id: UUID
    status: str
    summary: str | None = None
    processing_time_ms: int | None = None
    cached: bool = False
    error_message: str | None = None
