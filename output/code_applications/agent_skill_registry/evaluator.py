"""Evaluation helpers for agent skills and skill compositions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from registry import SkillRegistry


@dataclass
class EvaluationCase:
    """One evaluation input/output pair."""

    case_id: str
    input_text: str
    expected: Any
    metric: str = "exact"


class SkillEvaluator:
    """Run evaluations and feed the resulting scores back into the registry."""

    def evaluate_skill(self, registry: SkillRegistry, skill_name: str, cases: Iterable[EvaluationCase]) -> dict[str, float]:
        """Evaluate one registered skill."""
        scores: list[float] = []
        latencies: list[float] = []
        for case in cases:
            prediction, latency_ms = registry.execute(skill_name, case.input_text)
            score = self._score(case.metric, prediction, case.expected)
            registry.record_metric(skill_name, score=score, latency_ms=latency_ms)
            scores.append(score)
            latencies.append(latency_ms)
        return {
            "avg_score": float(sum(scores) / len(scores)),
            "avg_latency_ms": float(sum(latencies) / len(latencies)),
        }

    def evaluate_composition(
        self,
        registry: SkillRegistry,
        skill_names: list[str],
        cases: Iterable[EvaluationCase],
    ) -> dict[str, float]:
        """Evaluate a composed pipeline without registering it permanently."""
        pipeline = registry.compose(skill_names)
        scores: list[float] = []
        for case in cases:
            prediction = pipeline(case.input_text)
            scores.append(self._score(case.metric, prediction, case.expected))
        return {"avg_score": float(sum(scores) / len(scores)), "runs": float(len(scores))}

    def _score(self, metric: str, prediction: Any, expected: Any) -> float:
        """Score exact, contains, or Jaccard-style matches."""
        if metric == "exact":
            return float(str(prediction).strip().lower() == str(expected).strip().lower())
        if metric == "contains":
            return float(str(expected).strip().lower() in str(prediction).strip().lower())
        predicted = self._token_set(prediction)
        expected_tokens = self._token_set(expected)
        union = predicted | expected_tokens
        return float(len(predicted & expected_tokens) / len(union)) if union else 1.0

    @staticmethod
    def _token_set(value: Any) -> set[str]:
        """Convert a string or list into a token set."""
        if isinstance(value, list):
            return {str(item).lower() for item in value}
        return {token for token in str(value).lower().replace(",", " ").replace(".", " ").split() if token}


if __name__ == "__main__":
    print("Skill evaluator ready.")
