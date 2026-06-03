"""Registry for discovering, composing, and tracking agent skills."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import time
from typing import Any, Callable

import pandas as pd

SkillCallable = Callable[[str], Any]


@dataclass
class SkillMetrics:
    """Performance metrics tracked for one skill."""

    runs: int = 0
    avg_score: float = 0.0
    avg_latency_ms: float = 0.0
    last_score: float = 0.0

    def update(self, score: float, latency_ms: float) -> None:
        """Update rolling averages after one evaluation."""
        self.runs += 1
        self.avg_score += (score - self.avg_score) / self.runs
        self.avg_latency_ms += (latency_ms - self.avg_latency_ms) / self.runs
        self.last_score = score


@dataclass
class RegisteredSkill:
    """A skill stored in the registry."""

    name: str
    description: str
    tags: set[str]
    fn: SkillCallable
    metrics: SkillMetrics = field(default_factory=SkillMetrics)


class SkillRegistry:
    """Register, discover, compose, and score agent skills."""

    def __init__(self) -> None:
        self._skills: dict[str, RegisteredSkill] = {}

    def register(self, name: str, description: str, tags: set[str], fn: SkillCallable) -> None:
        """Add a skill to the registry.

        Raises
        ------
        ValueError
            If ``name`` is empty, ``description`` is empty, or ``fn`` is not callable.
        """
        if not name or not name.strip():
            raise ValueError("Skill name must be a non-empty string.")
        if not description or not description.strip():
            raise ValueError(f"Skill '{name}': description must be a non-empty string.")
        if not callable(fn):
            raise ValueError(f"Skill '{name}': fn must be callable, got {type(fn).__name__}.")
        if name in self._skills:
            raise ValueError(
                f"Skill '{name}' is already registered. Use a unique name or deregister it first."
            )
        self._skills[name] = RegisteredSkill(name=name, description=description, tags=tags, fn=fn)

    def deregister(self, name: str) -> None:
        """Remove a skill from the registry.

        Raises
        ------
        KeyError
            If no skill with ``name`` exists.
        """
        if name not in self._skills:
            raise KeyError(
                f"Skill '{name}' is not registered. Available skills: {sorted(self._skills)}"
            )
        del self._skills[name]

    def get(self, name: str) -> RegisteredSkill:
        """Retrieve one skill.

        Raises
        ------
        KeyError
            If no skill with ``name`` exists.
        """
        if name not in self._skills:
            raise KeyError(
                f"Skill '{name}' is not registered. Available skills: {sorted(self._skills)}"
            )
        return self._skills[name]

    def discover(self, required_tags: set[str] | None = None, query: str | None = None) -> list[RegisteredSkill]:
        """Find skills by tags or free-text query."""
        required_tags = required_tags or set()
        query_text = (query or "").lower()
        matches: list[RegisteredSkill] = []
        for skill in self._skills.values():
            haystack = f"{skill.name} {skill.description} {' '.join(sorted(skill.tags))}".lower()
            if required_tags and not required_tags.issubset(skill.tags):
                continue
            if query_text and query_text not in haystack:
                continue
            matches.append(skill)
        return sorted(matches, key=lambda skill: (-skill.metrics.avg_score, skill.name))

    def execute(self, name: str, text: str) -> tuple[Any, float]:
        """Run a skill and measure latency.

        Raises
        ------
        KeyError
            If ``name`` is not registered.
        TypeError
            If ``text`` is not a string.
        """
        if not isinstance(text, str):
            raise TypeError(
                f"Skill '{name}' expects a str input, got {type(text).__name__}."
            )
        start = time.perf_counter()
        result = self.get(name).fn(text)
        latency_ms = (time.perf_counter() - start) * 1000.0
        return result, latency_ms

    def record_metric(self, name: str, score: float, latency_ms: float) -> None:
        """Update tracked metrics for a skill.

        Raises
        ------
        ValueError
            If ``score`` is not in [0, 1] or ``latency_ms`` is negative.
        """
        if not (0.0 <= score <= 1.0):
            raise ValueError(
                f"score must be in [0, 1]; got {score!r} for skill '{name}'."
            )
        if latency_ms < 0.0:
            raise ValueError(
                f"latency_ms must be non-negative; got {latency_ms!r} for skill '{name}'."
            )
        self.get(name).metrics.update(score=score, latency_ms=latency_ms)

    def names(self) -> list[str]:
        """Return the names of all registered skills in sorted order."""
        return sorted(self._skills)

    def compose(self, skill_names: list[str], composite_name: str | None = None) -> Callable[[str], Any]:
        """Create a simple sequential composition of registered skills."""
        def pipeline(text: str) -> Any:
            current: Any = text
            for skill_name in skill_names:
                current_text = current if isinstance(current, str) else self._stringify(current)
                current, _ = self.execute(skill_name, current_text)
            return current

        pipeline.__name__ = composite_name or "_then_".join(skill_names)
        return pipeline

    def leaderboard(self) -> pd.DataFrame:
        """Return a sortable skill performance table."""
        rows = []
        for skill in self._skills.values():
            row = {
                "name": skill.name,
                "description": skill.description,
                "tags": ", ".join(sorted(skill.tags)),
                **asdict(skill.metrics),
            }
            rows.append(row)
        return pd.DataFrame(rows).sort_values(by=["avg_score", "runs"], ascending=[False, False]).reset_index(drop=True)

    @staticmethod
    def _stringify(value: Any) -> str:
        """Turn non-string outputs into a text representation."""
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return str(value)


if __name__ == "__main__":
    print("Agent skill registry ready.")
