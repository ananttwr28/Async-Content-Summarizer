from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.core.redis import get_redis, JOB_QUEUE_KEY
from app.models.job import Job
from app.schemas.summarize import SummarizeRequest
from app.schemas.job import JobSubmitResponse, JobStatusResponse, JobResultResponse
import redis

router = APIRouter()

@router.post("/submit", response_model=JobSubmitResponse)
def submit_job(
    request: SummarizeRequest,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    input_type = "url" if request.url else "text"
    input_value = request.url if request.url else request.text
    
    new_job = Job(
        input_type=input_type,
        input_value=input_value,
        status="queued"
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    # Push job ID to Redis queue
    redis_client.lpush(JOB_QUEUE_KEY, str(new_job.id))
    
    return JobSubmitResponse(
        job_id=new_job.id,
        status=new_job.status
    )

@router.get("/status/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: UUID, 
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        created_at=job.created_at
    )

@router.get("/result/{job_id}", response_model=JobResultResponse)
def get_job_result(
    job_id: UUID, 
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status == "completed":
        return JobResultResponse(
            job_id=job.id,
            status=job.status,
            summary=job.summary,
            processing_time_ms=job.processing_time_ms,
            cached=job.is_cached if job.is_cached else False
        )
    elif job.status == "failed":
        return JobResultResponse(
            job_id=job.id,
            status=job.status,
            error_message=job.error_message
        )
    else:
        return JobResultResponse(
            job_id=job.id,
            status=job.status,
            error_message="Job still processing" 
        )
