import time, redis
import asyncio
import hashlib
import json
import logging
from uuid import UUID
from datetime import datetime

from app.core.database import SessionLocal
from app.core.redis import get_redis, JOB_QUEUE_KEY
from app.models.job import Job
from app.services.summarizer import SummarizerService
from app.services.url_extractor import UrlExtractorService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

def get_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

async def process_job(job_id_str: str, summarizer: SummarizerService, extractor: UrlExtractorService):
    db = SessionLocal()
    redis_client = get_redis()
    
    try:
        job_id = UUID(job_id_str)
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            logger.error(f"Job {job_id} not found in database")
            return

        # Update status to processing
        job.status = "processing"
        job.updated_at = datetime.utcnow()
        db.commit()
        
        start_time = time.perf_counter()
        
        # 1. Resolve content
        try:
            if job.input_type == "url":
                content = await extractor.extract(job.input_value)
            else:
                content = job.input_value
        except Exception as e:
             # Extraction failed
             logger.error(f"Extraction failed for job {job_id}: {e}")
             job.status = "failed"
             job.error_message = f"Extraction failed: {str(e)}"
             job.updated_at = datetime.utcnow()
             db.commit()
             return

        # 2. Hash and Check Cache
        content_hash = get_content_hash(content)
        cache_key = f"summary_cache:{content_hash}"
        cached_summary = redis_client.get(cache_key)
        
        if cached_summary:
            logger.info(f"Cache hit for job {job_id}")
            job.summary = cached_summary
            job.status = "completed"
            job.is_cached = True
            job.processing_time_ms = 0 # Instant
        else:
            logger.info(f"Cache miss for job {job_id}. Calling LLM.")
            # 3. Call LLM
            try:
                summary = await summarizer.summarize(content)
                
                # Cache the result
                redis_client.set(cache_key, summary)
                
                job.summary = summary
                job.status = "completed"
                job.is_cached = False
                
                end_time = time.perf_counter()
                job.processing_time_ms = int((end_time - start_time) * 1000)
                
            except Exception as e:
                logger.error(f"Summarization failed for job {job_id}: {e}")
                job.status = "failed"
                job.error_message = f"Summarization failed: {str(e)}"
        
        job.updated_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        logger.exception(f"Unexpected error processing job {job_id_str}")
        try:
            if 'job' in locals() and job:
                job.status = "failed"
                job.error_message = "Internal worker error"
                db.commit()
        except:
            pass
    finally:
        db.close()

async def run_worker():
    print("Worker started. Waiting for jobs...")
    redis_client = get_redis()
    summarizer = SummarizerService()
    extractor = UrlExtractorService()
    
    while True:
        try:
            item = redis_client.brpop(JOB_QUEUE_KEY, timeout=5)
            
            if item:
                _, job_id = item
                logger.info(f"Picked up job: {job_id}")
                await process_job(job_id, summarizer, extractor)
            
        except redis.exceptions.ConnectionError:
            logger.error("Redis connection lost. Retrying in 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_worker())
