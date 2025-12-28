# Async Content Summarizer

An asynchronous content summarization service that accepts URLs or raw text, processes them in the background, and returns AI-generated summaries.

---

## Architecture Overview

- **FastAPI** – REST API layer  
- **PostgreSQL** – Persistent job storage  
- **Redis**
  - Queue (LIST) for async job processing
  - Cache for deduplicated summaries  
- **Background Worker** – Pulls jobs from Redis and processes them  
- **LLM** – Google Gemini (pluggable)

---

## High-Level Flow

1. Client submits text or URL  
2. API creates a job record in PostgreSQL  
3. Job ID is pushed to Redis queue  
4. Worker picks job and processes it  
5. Summary stored in DB and cached in Redis  
6. Client polls for status/result  

---

## API Endpoints

### POST /submit
Submit text or URL for summarization.

### GET /status/{job_id}
Check job status: queued | processing | completed | failed

### GET /result/{job_id}
Retrieve summary result when completed.

---

## Setup Instructions

### 1. Clone the repository
git clone <repo-url>  
cd async-content-summarizer  

### 2. Create virtual environment
python -m venv venv  
venv\Scripts\activate  

### 3. Install dependencies
pip install -r requirements.txt  

### 4. Configure environment
copy .env.example .env  

Fill in database, Redis, and API key values.

### 5. Start services
- PostgreSQL  
- Redis  

### 6. Run API
uvicorn app.main:app --reload  

### 7. Run worker
python worker.py  

---

## Notes

- Jobs are processed asynchronously  
- Redis queue ensures non-blocking API  
- Redis cache avoids duplicate summarization  
- Graceful handling of failures (invalid input, timeouts)
