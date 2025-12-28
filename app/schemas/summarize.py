from pydantic import BaseModel, Field, model_validator

class SummarizeRequest(BaseModel):
    text: str | None = Field(
        default=None,
        min_length=50, 
        max_length=12000, 
        description="Text content to summarize",
        examples=["This is a long text that needs to be summarized..."]
    )
    url: str | None = Field(
        default=None,
        description="URL to extract text from",
        examples=["https://example.com/article"]
    )

    @model_validator(mode='after')
    def check_text_or_url(self) -> 'SummarizeRequest':
        if not self.text and not self.url:
            raise ValueError('Either text or url must be provided')
        if self.text and self.url:
             raise ValueError('Provide either text or url, not both')
        return self

class SummarizeResponse(BaseModel):
    summary: str
    processing_time_ms: float
