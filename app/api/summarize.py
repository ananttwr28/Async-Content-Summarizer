import time
from fastapi import APIRouter, Depends
from app.schemas.summarize import SummarizeRequest, SummarizeResponse
from app.services.summarizer import SummarizerService

router = APIRouter()

def get_summarizer_service():
    return SummarizerService()

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(
    request: SummarizeRequest,
    service: SummarizerService = Depends(get_summarizer_service)
):
    start_time = time.perf_counter()
    summary = await service.summarize(request.text)
    end_time = time.perf_counter()
    
    processing_time_ms = (end_time - start_time) * 1000
    
    return SummarizeResponse(
        summary=summary,
        processing_time_ms=round(processing_time_ms, 2)
    )
