"""
Gemini API client for text improvement.
Handles API calls, rate limiting, and prompt engineering.
"""

import time
import logging
from typing import Optional, Dict
from collections import deque
import google.generativeai as genai


class GeminiClient:
    """Client for interacting with Google Gemini API."""

    # Prompt templates for different modes
    PROMPTS = {
        "grammar_fix": """Fix any grammar, spelling, and punctuation errors in the following text.
Maintain the original tone and style. Only return the corrected text, nothing else.

Text: {text}""",

        "formal": """Rewrite the following text in a more formal and professional style.
Maintain the core message. Only return the rewritten text, nothing else.

Text: {text}""",

        "casual": """Rewrite the following text in a more casual and friendly style.
Maintain the core message. Only return the rewritten text, nothing else.

Text: {text}""",

        "simplify": """Simplify the following text to make it clearer and easier to understand.
Use simpler words and shorter sentences. Only return the simplified text, nothing else.

Text: {text}""",

        "expand": """Expand and elaborate on the following text with more detail and context.
Maintain the original style. Only return the expanded text, nothing else.

Text: {text}"""
    }

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp",
                 requests_per_minute: int = 50, max_retries: int = 3,
                 timeout: int = 10):
        """
        Initialize Gemini client.

        Args:
            api_key: Google Gemini API key
            model: Model name to use
            requests_per_minute: Rate limit for API calls
            max_retries: Maximum retry attempts for failed requests
            timeout: Request timeout in seconds
        """
        self.logger = logging.getLogger(__name__)
        self.max_retries = max_retries
        self.timeout = timeout

        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

        # Rate limiting setup
        self.requests_per_minute = requests_per_minute
        self.request_times = deque(maxlen=requests_per_minute)

        self.logger.info(f"Gemini client initialized with model: {model}")

    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        now = time.time()

        # Remove requests older than 1 minute
        while self.request_times and now - self.request_times[0] > 60:
            self.request_times.popleft()

        # If at limit, wait
        if len(self.request_times) >= self.requests_per_minute:
            wait_time = 60 - (now - self.request_times[0])
            if wait_time > 0:
                self.logger.warning(f"Rate limit reached. Waiting {wait_time:.2f}s")
                time.sleep(wait_time)

        self.request_times.append(time.time())

    def improve_text(self, text: str, mode: str = "grammar_fix") -> Optional[str]:
        """
        Improve text using Gemini API.

        Args:
            text: Text to improve
            mode: Improvement mode (grammar_fix, formal, casual, simplify, expand)

        Returns:
            Improved text or None if failed
        """
        if not text or not text.strip():
            self.logger.warning("Empty text provided")
            return None

        if mode not in self.PROMPTS:
            self.logger.error(f"Invalid mode: {mode}")
            return None

        # Apply rate limiting
        self._check_rate_limit()

        # Build prompt
        prompt = self.PROMPTS[mode].format(text=text)

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Sending request (attempt {attempt + 1}/{self.max_retries})")

                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.3,  # Lower temperature for more consistent corrections
                        "max_output_tokens": 2048,
                    }
                )

                if response.text:
                    improved_text = response.text.strip()
                    self.logger.info(f"Successfully improved text ({mode})")
                    return improved_text
                else:
                    self.logger.warning("Empty response from Gemini")

            except Exception as e:
                self.logger.error(f"API error (attempt {attempt + 1}): {str(e)}")

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    self.logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)

        self.logger.error("All retry attempts failed")
        return None

    def get_available_modes(self) -> Dict[str, str]:
        """
        Get available improvement modes with descriptions.

        Returns:
            Dictionary of mode names and descriptions
        """
        return {
            "grammar_fix": "Fix grammar, spelling, and punctuation",
            "formal": "Make more formal and professional",
            "casual": "Make more casual and friendly",
            "simplify": "Simplify and clarify",
            "expand": "Expand with more detail"
        }
