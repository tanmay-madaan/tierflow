import asyncio
import time
from typing import Optional, Dict, Any
import aiohttp
from config import API_KEY, LLM_BASE_URL, LLM_TIMEOUT, LLM_MAX_RETRIES, get_active_api_key, get_base_url

class LLMClientError(Exception):
    """Base exception for LLM API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, error_type: str = "ProviderError"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type


class LLMClient:
    """
    OpenAI-compatible async HTTP client for real LLM inference.
    Supports Google Gemini (via Google AI Studio), OpenAI, Groq, Ollama, OpenRouter, and compatible endpoints.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        session: Optional[aiohttp.ClientSession] = None
    ):
        self.api_key = api_key
        self.base_url_override = base_url
        self.timeout = timeout if timeout is not None else LLM_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else LLM_MAX_RETRIES
        self._external_session = session

    @property
    def base_url(self) -> str:
        return (self.base_url_override if self.base_url_override is not None else get_base_url()).rstrip('/')

    def _is_local_endpoint(self) -> bool:
        """Check if base_url is localhost (e.g., Ollama or vLLM), where api_key is not strictly required."""
        return "localhost" in self.base_url or "127.0.0.1" in self.base_url

    async def chat_completion(
        self,
        model_id: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 512
    ) -> Dict[str, Any]:
        """
        Execute chat completion request with structured telemetry and safe error handling.
        """
        active_key = self.api_key if self.api_key is not None else get_active_api_key()

        # Validate credentials for remote APIs
        if not active_key and not self._is_local_endpoint():
            return {
                "response": "",
                "model_id": model_id,
                "latency": 0.0,
                "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "retry_attempts": 0,
                "retry_time": 0.0,
                "error": {
                    "type": "AuthenticationError",
                    "message": "Missing API key. Configure GEMINI_API_KEY (recommended) or LLM_API_KEY in backend/.env for real inference.",
                    "status_code": 401
                }
            }

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        if active_key:
            headers["Authorization"] = f"Bearer {active_key}"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        retries_done = 0
        total_retry_time = 0.0
        start_time = time.perf_counter()

        timeout_obj = aiohttp.ClientTimeout(total=self.timeout)
        own_session = self._external_session is None
        session = self._external_session or aiohttp.ClientSession(timeout=timeout_obj)

        try:
            for attempt in range(self.max_retries + 1):
                try:
                    attempt_start = time.perf_counter()
                    async with session.post(url, headers=headers, json=payload) as resp:
                        status = resp.status
                        if status == 200:
                            data = await resp.json()
                            elapsed = time.perf_counter() - start_time
                            choices = data.get("choices", [])
                            content = ""
                            if choices and isinstance(choices[0], dict):
                                msg = choices[0].get("message", {})
                                if isinstance(msg, dict):
                                    content = msg.get("content") or ""
                            usage = data.get("usage", {})
                            return {
                                "response": content,
                                "model_id": data.get("model", model_id),
                                "latency": elapsed,
                                "token_usage": {
                                    "prompt_tokens": usage.get("prompt_tokens", 0),
                                    "completion_tokens": usage.get("completion_tokens", 0),
                                    "total_tokens": usage.get("total_tokens", 0)
                                },
                                "retry_attempts": retries_done,
                                "retry_time": total_retry_time,
                                "error": None
                            }

                        body_text = await resp.text()
                        # Transient errors: 429 rate limit or 5xx server errors
                        if (status == 429 or status >= 500) and attempt < self.max_retries:
                            backoff = 0.5 * (2 ** attempt)
                            retries_done += 1
                            total_retry_time += backoff
                            await asyncio.sleep(backoff)
                            continue

                        # Non-transient or retries exhausted
                        elapsed = time.perf_counter() - start_time
                        error_type = "RateLimitError" if status == 429 else (
                            "AuthenticationError" if status == 401 else "APIStatusError"
                        )
                        return {
                            "response": "",
                            "model_id": model_id,
                            "latency": elapsed,
                            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                            "retry_attempts": retries_done,
                            "retry_time": total_retry_time,
                            "error": {
                                "type": error_type,
                                "message": f"HTTP {status}: {body_text[:300]}",
                                "status_code": status
                            }
                        }

                except asyncio.TimeoutError:
                    if attempt < self.max_retries:
                        backoff = 0.5 * (2 ** attempt)
                        retries_done += 1
                        total_retry_time += backoff
                        await asyncio.sleep(backoff)
                        continue
                    elapsed = time.perf_counter() - start_time
                    return {
                        "response": "",
                        "model_id": model_id,
                        "latency": elapsed,
                        "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                        "retry_attempts": retries_done,
                        "retry_time": total_retry_time,
                        "error": {
                            "type": "TimeoutError",
                            "message": f"Request timed out after {self.timeout}s",
                            "status_code": 408
                        }
                    }
                except aiohttp.ClientError as ce:
                    if attempt < self.max_retries:
                        backoff = 0.5 * (2 ** attempt)
                        retries_done += 1
                        total_retry_time += backoff
                        await asyncio.sleep(backoff)
                        continue
                    elapsed = time.perf_counter() - start_time
                    return {
                        "response": "",
                        "model_id": model_id,
                        "latency": elapsed,
                        "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                        "retry_attempts": retries_done,
                        "retry_time": total_retry_time,
                        "error": {
                            "type": "NetworkError",
                            "message": str(ce),
                            "status_code": 503
                        }
                    }
        finally:
            if own_session:
                await session.close()
