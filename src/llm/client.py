from openai import OpenAI
import os
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. LLM calls will fail unless a local base_url is used without auth.")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        self.model = model

    def generate_summary(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates a summary using the LLM.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0  # Deterministic output
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            return f"Error generating summary: {e}"
