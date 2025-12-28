import redis
from app.core.config import settings

# Create a Redis client instance
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

JOB_QUEUE_KEY = "summary_jobs"

def get_redis():
    return redis_client
