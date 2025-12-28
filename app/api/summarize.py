import time
from fastapi import APIRouter, Depends
from app.schemas.summarize import SummarizeRequest, SummarizeResponse
from app.services.summarizer import SummarizerService
from app.services.url_extractor import UrlExtractorService

router = APIRouter()

def get_summarizer_service():
    return SummarizerService()

def get_url_extractor_service():
    return UrlExtractorService()

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(
    request: SummarizeRequest,
    summarizer_service: SummarizerService = Depends(get_summarizer_service),
    extractor_service: UrlExtractorService = Depends(get_url_extractor_service)
):
    start_time = time.perf_counter()
    
    if request.url:
        text_to_summarize = await extractor_service.extract(request.url)
    else:
        text_to_summarize = request.text
        
    summary = await summarizer_service.summarize(text_to_summarize)
    end_time = time.perf_counter()
    
    processing_time_ms = (end_time - start_time) * 1000
    
    return SummarizeResponse(
        summary=summary,
        processing_time_ms=round(processing_time_ms, 2)
    )
