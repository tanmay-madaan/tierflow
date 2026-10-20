from abc import ABC, abstractmethod
import asyncio
import random
import time
from typing import Optional, Dict, Any
from config import MODEL_TIERS
from .client import LLMClient

class ModelProvider(ABC):
    """
    Abstract base provider with unified support for:
      1. Explicit execution mode ('demo' vs 'real')
      2. Transparent token-based cost accounting
      3. Real OpenAI-compatible inference via LLMClient
      4. Safe error handling (never silently faking real inference failures)
    """
    name: str
    tier: str
    model_id: str
    client: Optional[LLMClient] = None

    def __init__(self, client: Optional[LLMClient] = None):
        tier_cfg = MODEL_TIERS.get(self.tier, {})
        self.model_id = tier_cfg.get('model_id', f'{self.tier.lower()}-default')
        self.client = client or LLMClient()

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate inference cost in USD based on transparent tier pricing."""
        tier_cfg = MODEL_TIERS.get(self.tier, {})
        input_rate = tier_cfg.get('input_cost_per_token', 0.000001)
        output_rate = tier_cfg.get('output_cost_per_token', 0.000002)
        return float(prompt_tokens * input_rate + completion_tokens * output_rate)

    @abstractmethod
    def simulate_response(self, query: str) -> str:
        """Generate a realistic contextual demo response."""
        pass

    async def generate(
        self,
        query: str,
        demo_mode: bool = True,
        execution_mode: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 512
    ) -> Dict[str, Any]:
        """
        Unified generation endpoint returning structured inference measurements.
        """
        # Determine explicit execution mode
        is_demo = (execution_mode == "demo") if execution_mode is not None else demo_mode
        active_mode = "demo" if is_demo else "real"

        if is_demo:
            # DEMO MODE: Simulated execution
            tier_cfg = MODEL_TIERS.get(self.tier, {})
            lat_range = tier_cfg.get('latency_range', (0.1, 0.3))
            sim_latency = random.uniform(*lat_range)
            # Brief async sleep to emulate asynchronous I/O
            await asyncio.sleep(min(0.08, sim_latency * 0.2))

            resp_text = self.simulate_response(query)

            # Estimate token counts for telemetry
            prompt_tokens = max(1, int(len(query.split()) * 1.3))
            completion_tokens = max(1, int(len(resp_text.split()) * 1.3))
            cost = self.calculate_cost(prompt_tokens, completion_tokens)

            return {
                "response": resp_text,
                "selected_model": self.tier,
                "model_id": f"demo-{self.tier.lower()}-simulated",
                "latency": round(sim_latency, 4),
                "token_usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                "estimated_cost": round(cost, 8),
                "execution_mode": "demo",
                "error": None
            }

        # REAL MODE: Live API inference
        result = await self.client.chat_completion(
            model_id=self.model_id,
            prompt=query,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

        token_usage = result.get("token_usage", {})
        prompt_tokens = token_usage.get("prompt_tokens", 0)
        completion_tokens = token_usage.get("completion_tokens", 0)
        cost = self.calculate_cost(prompt_tokens, completion_tokens)

        return {
            "response": result.get("response", ""),
            "selected_model": self.tier,
            "model_id": result.get("model_id", self.model_id),
            "latency": round(result.get("latency", 0.0), 4),
            "token_usage": token_usage,
            "estimated_cost": round(cost, 8),
            "execution_mode": "real",
            "retry_attempts": result.get("retry_attempts", 0),
            "retry_time": round(result.get("retry_time", 0.0), 4),
            "error": result.get("error")
        }
