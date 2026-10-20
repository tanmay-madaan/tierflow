from typing import Optional, Dict, Any
from config import CONFIDENCE_THRESHOLD

class Router:
    """
    Adaptive model tier router supporting:
      1. Confidence-Aware Routing Policy (validation-calibrated tier thresholds)
      2. Legacy single-threshold escalation baseline (flat 0.50 bump)
      3. Explicit empty query and non-text edge-case guards
      4. Structured observability telemetry (initial_model, was_escalated, escalation_reason)
    """
    def __init__(
        self,
        classifier,
        feature_extractor,
        policy: str = "confidence_aware",
        threshold_small: float = 0.60,
        threshold_medium: float = 0.40,
        legacy_threshold: float = CONFIDENCE_THRESHOLD
    ):
        self.classifier = classifier
        self.fe = feature_extractor
        self.tier_order = ['SMALL', 'MEDIUM', 'LARGE']
        self.policy = policy
        self.threshold_small = threshold_small
        self.threshold_medium = threshold_medium
        self.legacy_threshold = legacy_threshold

    def route(self, query: str, policy: Optional[str] = None) -> Dict[str, Any]:
        # Explicit guard for empty or whitespace-only inputs:
        # Do not rely on linear model softmax (which defaults to high-confidence SMALL on empty inputs).
        if not query or not query.strip():
            features = self.fe.extract(query or "")
            return {
                'selected_model': 'MEDIUM',
                'initial_model': 'UNKNOWN',
                'confidence': 0.0,
                'was_escalated': True,
                'escalation_reason': 'Empty query or zero valid tokens; routed to safe fallback tier (MEDIUM).',
                'complexity': 'LOW',
                'features': features,
                'reasoning': 'Query is empty. Routed to safe fallback tier (MEDIUM).',
                'probabilities': {'SMALL': 0.0, 'MEDIUM': 1.0, 'LARGE': 0.0}
            }

        features = self.fe.extract(query)
        pred = self.classifier.predict(query)
        
        initial_model = pred['selected_model']
        confidence = float(pred['confidence'])
        probabilities = pred.get('probabilities', {})
        
        active_policy = policy or self.policy
        selected_model = initial_model
        was_escalated = False
        escalation_reason = None

        if active_policy == "confidence_aware":
            # Tier-specific risk thresholds calibrated on validation split:
            # - SMALL requires confidence >= threshold_small (0.60) to avoid false-small routing
            # - MEDIUM requires confidence >= threshold_medium (0.40) before escalating to LARGE
            p_small = float(probabilities.get('SMALL', 0.0))
            p_medium = float(probabilities.get('MEDIUM', 0.0))
            p_large = float(probabilities.get('LARGE', 0.0))

            if initial_model == 'SMALL' and (p_small < self.threshold_small or confidence < self.threshold_small):
                was_escalated = True
                if p_large > p_medium:
                    selected_model = 'LARGE'
                    escalation_reason = f"P(SMALL)={p_small:.3f} below threshold {self.threshold_small:.2f} and P(LARGE)={p_large:.3f} > P(MEDIUM); escalated to LARGE."
                else:
                    selected_model = 'MEDIUM'
                    escalation_reason = f"P(SMALL)={p_small:.3f} below threshold {self.threshold_small:.2f}; escalated to MEDIUM."
            elif initial_model == 'MEDIUM' and (p_medium < self.threshold_medium or confidence < self.threshold_medium):
                was_escalated = True
                selected_model = 'LARGE'
                escalation_reason = f"P(MEDIUM)={p_medium:.3f} below threshold {self.threshold_medium:.2f}; escalated to LARGE."
            elif initial_model == 'LARGE':
                was_escalated = False
                escalation_reason = None
        else:
            # Legacy single-threshold policy (flat 0.50 cutoff)
            if confidence < self.legacy_threshold:
                idx = self.tier_order.index(selected_model)
                if idx < len(self.tier_order) - 1:
                    new_model = self.tier_order[idx + 1]
                    was_escalated = True
                    escalation_reason = f"Confidence {confidence:.3f} below {self.legacy_threshold:.2f}, bumping up from {selected_model} to {new_model}."
                    selected_model = new_model

        reasoning = f"Model predicted {initial_model} with {confidence*100:.1f}% confidence."
        if was_escalated and escalation_reason:
            reasoning += f" Escalated to {selected_model}: {escalation_reason}"
        reasoning += f" Query complexity estimated as {features['estimated_complexity']}."

        return {
            'selected_model': selected_model,
            'initial_model': initial_model,
            'confidence': confidence,
            'was_escalated': was_escalated,
            'escalation_reason': escalation_reason,
            'complexity': features['estimated_complexity'],
            'features': features,
            'reasoning': reasoning,
            'probabilities': probabilities
        }
