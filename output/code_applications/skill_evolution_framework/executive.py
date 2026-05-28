"""Executive strategy for selecting and composing agent skills."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from skills import SkillLibrary


@dataclass
class TextTask:
    """A simple text-processing task."""

    task_id: str
    task_type: str
    text: str
    expected: Any


@dataclass
class ExecutionTrace:
    """The executive's selected plan and final output for one task."""

    task_id: str
    selected_skills: list[str]
    result: Any
    context: dict[str, Any]


class ExecutiveStrategy:
    """Select skill chains based on task type and learned preferences."""

    def __init__(self, task_recipes: dict[str, list[list[str]]] | None = None) -> None:
        self.task_recipes = task_recipes or {
            "summarize": [
                ["normalize_text", "split_sentences", "summarize_text"],
                ["normalize_text", "split_sentences", "extract_keywords", "summarize_text"],
            ],
            "keywords": [
                ["normalize_text", "extract_keywords"],
                ["normalize_text", "remove_stopwords", "extract_keywords"],
            ],
            "sentiment": [["normalize_text", "classify_sentiment"]],
        }
        self.skill_weights: dict[str, float] = {}

    def choose_plan(self, task: TextTask) -> list[str]:
        """Pick the highest-scoring chain for the task type."""
        candidates = self.task_recipes.get(task.task_type, [["normalize_text"]])
        return max(candidates, key=self._plan_score)

    def _plan_score(self, chain: list[str]) -> float:
        """Score a candidate chain with simple learned weights."""
        return float(sum(self.skill_weights.get(skill_name, 0.0) for skill_name in chain))

    def execute(self, task: TextTask, library: SkillLibrary, chain: list[str] | None = None) -> ExecutionTrace:
        """Run the selected or supplied chain on the task."""
        plan = chain or self.choose_plan(task)
        context: dict[str, Any] = {"task_id": task.task_id, "task_type": task.task_type}
        for skill_name in plan:
            library.get(skill_name).apply(task.text, context)
        result = context.get("result")
        if result is None:
            result = context.get("normalized_text") or context.get("keywords")
        return ExecutionTrace(task_id=task.task_id, selected_skills=plan, result=result, context=context)

    def promote_chain(self, task_type: str, chain: list[str]) -> None:
        """Move a stronger chain to the front of the recipe list."""
        existing = self.task_recipes.get(task_type, [])
        updated = [candidate for candidate in existing if candidate != chain]
        self.task_recipes[task_type] = [chain, *updated]

    def boost_chain(self, chain: list[str], delta: float = 0.25) -> None:
        """Increase weights for skills that participated in a good plan."""
        for skill_name in chain:
            self.skill_weights[skill_name] = self.skill_weights.get(skill_name, 0.0) + delta


if __name__ == "__main__":
    print("Executive strategy ready.")
