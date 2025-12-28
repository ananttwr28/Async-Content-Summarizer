import httpx
from readability import Document
from bs4 import BeautifulSoup
from fastapi import HTTPException, status
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class UrlExtractorService:
    async def extract(self, url: str) -> str:
        """
        Fetches the content from the given URL, extracts the main article text,
        cleans it, and returns the plain text.
        """
        try:
            headers = {
                "User-Agent": settings.SCRAPER_USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/"
            }
            async with httpx.AsyncClient(follow_redirects=True, timeout=settings.SCRAPER_TIMEOUT_SECONDS, headers=headers) as client:
                response = await client.get(url)
                
            if response.status_code != 200:
                logger.warning(f"URL fetch failed {url}: {response.status_code}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to fetch content from URL. Status code: {response.status_code}"
                )
                
            # Use readability to extract main content
            doc = Document(response.text)
            summary_html = doc.summary()
            
            if not summary_html:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Could not extract content from the page"
                )

            # Clean with BeautifulSoup
            soup = BeautifulSoup(summary_html, "html.parser")
            
            # Remove scripts, styles, and other non-content tags
            for element in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav"]):
                element.decompose()
                
            text = soup.get_text(separator=' ', strip=True)
            
            if not text or len(text) < 50:
                 raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Extracted content is too short or empty"
                )
                
            # Limit to 12,000 characters
            return text[:12000]

        except httpx.InvalidURL:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL format provided"
            )
        except httpx.RequestError as e:
             logger.error(f"Network error fetching {url}: {e}")
             raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to connect to the provided URL"
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.exception(f"Unexpected extraction error for {url}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Failed to process page content"
            )
