from pydantic import BaseModel, Field

class SummarizeRequest(BaseModel):
    text: str = Field(
        ..., 
        min_length=50, 
        max_length=12000, 
        description="Text content to summarize",
        examples=["This is a long text that needs to be summarized. It must be at least 50 characters long..."]
    )

class SummarizeResponse(BaseModel):
    summary: str
    processing_time_ms: float
