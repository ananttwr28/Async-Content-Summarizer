import logging, time
from fastapi import HTTPException, status
from app.services.llm_client import GeminiLLMClient

logger = logging.getLogger(__name__)

class SummarizerService:
    def __init__(self):
        self.llm_client = GeminiLLMClient()

    async def summarize(self, text: str) -> str:
        try:
            return await self.llm_client.summarize(text)

        except ValueError as e:
            logger.error(f"Value error in summarizer service: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Summarization service failed: {str(e)}"
            )

        except ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not connect to summarization service"
            )

        except TimeoutError as e:
            logger.error(f"Timeout error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Summarization request timed out"
            )

        except RuntimeError as e:
            logger.error(f"Runtime error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Summarization service encountered an error"
            )
            
        except Exception as e:
            logger.exception("Unexpected error in summarizer service")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during summarization"
            )
