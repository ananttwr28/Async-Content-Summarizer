from abc import ABC, abstractmethod
from openai import AsyncOpenAI
import openai
from app.core.config import settings

class LLMClient(ABC):
    @abstractmethod
    async def summarize(self, text: str) -> str:
        """Summarize the given text."""
        pass

class OpenAILLMClient(LLMClient):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            # We will handle this error in the service layer or let it bubble up, 
            # but usually it's best to fail early if possible, or fail at request time.
            # However, for now we will check at request time or initialize client with None 
            # and let OpenAI SDK throw error? 
            # The prompt says "Handle missing API key... cleanly".
            pass
        
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def summarize(self, text: str) -> str:
        if not settings.OPENAI_API_KEY:
             raise ValueError("OpenAI API key is missing. Please set OPENAI_API_KEY environment variable.")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": f"Summarize the following text clearly and concisely in 5–7 sentences:\n\n{text}"}
                ],
                max_tokens=500, # Reasonable limit for summary
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Received empty response from OpenAI")
                
            return content.strip()
            
        except openai.APIConnectionError as e:
            raise ConnectionError(f"Connection error to OpenAI: {e}")
        except openai.APITimeoutError as e:
            raise TimeoutError(f"OpenAI request timed out: {e}")
        except openai.AuthenticationError as e:
            raise ValueError(f"OpenAI authentication failed: {e}")
        except openai.APIError as e:
            raise RuntimeError(f"OpenAI API returned an error: {e}")

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

class GeminiLLMClient(LLMClient):
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL

    async def summarize(self, text: str) -> str:
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key is missing. Please set GEMINI_API_KEY environment variable.")

        try:
            model = genai.GenerativeModel(self.model_name)
            prompt = f"Summarize the following text clearly and concisely in 5–7 sentences:\n\n{text}"
            
            response = await model.generate_content_async(prompt)
            
            if not response.text:
                 raise ValueError("Received empty response from Gemini")
            
            return response.text.strip()

        except google_exceptions.ServiceUnavailable as e:
            raise ConnectionError(f"Gemini service unavailable: {e}")
        except google_exceptions.DeadlineExceeded as e:
            raise TimeoutError(f"Gemini request timed out: {e}")
        except google_exceptions.Unauthenticated as e:
            raise ValueError(f"Gemini authentication failed: {e}")
        except google_exceptions.GoogleAPICallError as e:
            raise RuntimeError(f"Gemini API returned an error: {e}")
        except Exception as e:
            
            if "UserLocation" in str(e) or "stop" in str(e): 
                 pass
            raise RuntimeError(f"Gemini processing failed (possibly safety block or other): {e}")
