"""Optimization loop for evolving skill compositions with validation gating."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

import pandas as pd

from executive import ExecutiveStrategy, TextTask
from skills import SkillLibrary


@dataclass
class OptimizationStep:
    """A record of one bounded skill-edit attempt."""

    epoch: int
    task_type: str
    candidate_chain: list[str]
    train_score: float
    validation_score: float
    accepted: bool


class SkillOptimizer:
    """A simplified SkillOpt-style loop using bounded composition updates."""

    def __init__(self, library: SkillLibrary, executive: ExecutiveStrategy) -> None:
        self.library = library
        self.executive = executive

    def evaluate_task(self, task: TextTask, chain: list[str] | None = None) -> tuple[float, Any]:
        """Execute one task and score the result against its expected output."""
        trace = self.executive.execute(task, self.library, chain=chain)
        return self._score(task, trace.result), trace.result

    def evaluate_dataset(self, tasks: Iterable[TextTask], chain_overrides: dict[str, list[str]] | None = None) -> pd.DataFrame:
        """Evaluate a batch of tasks and return detailed results."""
        rows: list[dict[str, Any]] = []
        for task in tasks:
            chain = None if chain_overrides is None else chain_overrides.get(task.task_type)
            score, prediction = self.evaluate_task(task, chain=chain)
            rows.append(
                {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "prediction": prediction,
                    "score": score,
                    "chain": " -> ".join(chain or self.executive.choose_plan(task)),
                }
            )
        return pd.DataFrame(rows)

    def optimize(
        self,
        train_tasks: list[TextTask],
        validation_tasks: list[TextTask],
        epochs: int = 2,
    ) -> list[OptimizationStep]:
        """Search small composition edits and keep only validation-approved improvements."""
        history: list[OptimizationStep] = []
        task_types = sorted({task.task_type for task in train_tasks})
        for epoch in range(1, epochs + 1):
            for task_type in task_types:
                current_chain = self.executive.task_recipes[task_type][0]
                candidates = self._candidate_chains(task_type)
                best_candidate = current_chain
                best_train_score = self._mean_score(train_tasks, task_type, current_chain)
                for candidate in candidates:
                    train_score = self._mean_score(train_tasks, task_type, candidate)
                    if train_score > best_train_score + 1e-9:
                        best_train_score = train_score
                        best_candidate = candidate

                current_validation = self._mean_score(validation_tasks, task_type, current_chain)
                candidate_validation = self._mean_score(validation_tasks, task_type, best_candidate)
                accepted = candidate_validation >= current_validation + 1e-9 and best_candidate != current_chain
                if accepted:
                    self.executive.promote_chain(task_type, best_candidate)
                    self.executive.boost_chain(best_candidate)
                history.append(
                    OptimizationStep(
                        epoch=epoch,
                        task_type=task_type,
                        candidate_chain=best_candidate,
                        train_score=best_train_score,
                        validation_score=candidate_validation,
                        accepted=accepted,
                    )
                )
        return history

    def history_frame(self, history: list[OptimizationStep]) -> pd.DataFrame:
        """Convert optimization steps to a DataFrame."""
        return pd.DataFrame([asdict(step) for step in history])

    def _candidate_chains(self, task_type: str) -> list[list[str]]:
        """Return small bounded edits for a task type."""
        built_ins = {
            "summarize": [
                ["normalize_text", "split_sentences", "summarize_text"],
                ["normalize_text", "split_sentences", "extract_keywords", "summarize_text"],
                ["normalize_text", "remove_stopwords", "extract_keywords", "split_sentences", "summarize_text"],
            ],
            "keywords": [
                ["normalize_text", "extract_keywords"],
                ["normalize_text", "remove_stopwords", "extract_keywords"],
            ],
            "sentiment": [["normalize_text", "classify_sentiment"]],
        }
        return built_ins.get(task_type, self.executive.task_recipes.get(task_type, []))

    def _mean_score(self, tasks: list[TextTask], task_type: str, chain: list[str]) -> float:
        """Compute mean score for one task type and one candidate chain."""
        relevant = [task for task in tasks if task.task_type == task_type]
        if not relevant:
            return 0.0
        scores = [self.evaluate_task(task, chain=chain)[0] for task in relevant]
        return float(sum(scores) / len(scores))

    def _score(self, task: TextTask, prediction: Any) -> float:
        """Score predictions for summary, keyword, and sentiment tasks."""
        if task.task_type == "sentiment":
            return float(str(prediction).strip().lower() == str(task.expected).strip().lower())
        if task.task_type == "keywords":
            predicted = {str(token).lower() for token in prediction}
            expected = {str(token).lower() for token in task.expected}
            union = predicted | expected
            return float(len(predicted & expected) / len(union)) if union else 1.0
        predicted_tokens = self._token_set(str(prediction))
        expected_tokens = self._token_set(str(task.expected))
        if not predicted_tokens or not expected_tokens:
            return 0.0
        precision = len(predicted_tokens & expected_tokens) / len(predicted_tokens)
        recall = len(predicted_tokens & expected_tokens) / len(expected_tokens)
        if precision + recall == 0:
            return 0.0
        return float(2 * precision * recall / (precision + recall))

    @staticmethod
    def _token_set(text: str) -> set[str]:
        """Normalize text into a token set for overlap scoring."""
        return {token for token in text.lower().replace(".", " ").replace(",", " ").split() if token}


if __name__ == "__main__":
    print("Skill optimizer ready.")
