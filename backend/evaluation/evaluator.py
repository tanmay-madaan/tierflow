import random

class QualityEvaluator:
    def evaluate(self, query: str, response: str, model_tier: str, demo_mode: bool) -> dict:
        if demo_mode:
            # Simulate scores
            base = 5.0
            if model_tier == 'SMALL':
                base = random.uniform(5.5, 7.5)
            elif model_tier == 'MEDIUM':
                base = random.uniform(6.5, 8.5)
            elif model_tier == 'LARGE':
                base = random.uniform(8.0, 9.5)
                
            return {
                "correctness": min(10.0, base + random.uniform(-0.5, 0.5)),
                "relevance": min(10.0, base + random.uniform(-0.5, 0.5)),
                "completeness": min(10.0, base + random.uniform(-1.0, 1.0)),
                "reasoning_quality": min(10.0, base + random.uniform(-1.0, 1.0)),
                "overall_score": base
            }
        else:
            # For real interactive queries without ground-truth reference answers,
            # do not assign an unverified hardcoded score. Quality is unmeasured.
            return {
                "correctness": None,
                "relevance": None,
                "completeness": None,
                "reasoning_quality": None,
                "overall_score": None
            }
