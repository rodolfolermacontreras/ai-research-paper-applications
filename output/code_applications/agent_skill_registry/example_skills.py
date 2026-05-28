"""Example usage of the agent skill registry."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

import matplotlib.pyplot as plt

from evaluator import EvaluationCase, SkillEvaluator
from registry import SkillRegistry

STOPWORDS = {"a", "an", "and", "for", "in", "of", "the", "to", "with"}
POSITIVE_WORDS = {"excellent", "fast", "great", "helpful", "reliable", "smooth"}
NEGATIVE_WORDS = {"bad", "buggy", "confusing", "slow", "terrible"}


def normalize_text(text: str) -> str:
    """Lowercase and collapse whitespace."""
    return " ".join(text.lower().split())


def extract_keywords(text: str) -> list[str]:
    """Return a few frequent content words."""
    tokens = [token for token in re.findall(r"[a-zA-Z']+", text.lower()) if token not in STOPWORDS and len(token) > 2]
    return [word for word, _ in Counter(tokens).most_common(4)]


def first_sentence_summary(text: str) -> str:
    """Return the leading sentence as a cheap baseline summary."""
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    return sentences[0] if sentences else text.strip()


def sentiment_label(text: str) -> str:
    """Assign a coarse sentiment label."""
    tokens = re.findall(r"[a-zA-Z']+", text.lower())
    positive = sum(token in POSITIVE_WORDS for token in tokens)
    negative = sum(token in NEGATIVE_WORDS for token in tokens)
    if positive > negative:
        return "positive"
    if negative > positive:
        return "negative"
    return "neutral"


def main() -> None:
    """Register sample skills, evaluate them, and save a leaderboard plot."""
    app_dir = Path(__file__).resolve().parent
    output_dir = app_dir / "artifacts"
    output_dir.mkdir(exist_ok=True)

    registry = SkillRegistry()
    evaluator = SkillEvaluator()

    registry.register("normalize_text", "Normalize casing and whitespace.", {"cleanup", "text"}, normalize_text)
    registry.register("extract_keywords", "Extract keyword candidates.", {"analysis", "keywords", "text"}, extract_keywords)
    registry.register("first_sentence_summary", "Return the first sentence as a summary.", {"summary", "text"}, first_sentence_summary)
    registry.register("sentiment_label", "Assign positive, negative, or neutral sentiment.", {"analysis", "sentiment", "text"}, sentiment_label)

    discovered = registry.discover(required_tags={"analysis"})
    print("Discovered analysis skills:")
    for skill in discovered:
        print(f"- {skill.name}: {skill.description}")

    keyword_cases = [
        EvaluationCase("kw-1", "The registry tracks latency, accuracy, and reliability for each skill.", ["registry", "latency", "accuracy", "reliability"], metric="jaccard"),
        EvaluationCase("kw-2", "Generalization monitors plot loss, gap, and effective dimension.", ["generalization", "monitors", "loss", "dimension"], metric="jaccard"),
    ]
    summary_cases = [
        EvaluationCase("sum-1", "Release note. Validation gating improved the optimizer. More benchmarks arrive tomorrow.", "Release note.", metric="contains"),
        EvaluationCase("sum-2", "Daily log. The most important finding was reduced latency. Cleanup continues.", "Daily log.", metric="contains"),
    ]
    sentiment_cases = [
        EvaluationCase("sent-1", "The rollout was smooth and excellent.", "positive"),
        EvaluationCase("sent-2", "The interface felt buggy and slow.", "negative"),
    ]

    keyword_result = evaluator.evaluate_skill(registry, "extract_keywords", keyword_cases)
    summary_result = evaluator.evaluate_skill(registry, "first_sentence_summary", summary_cases)
    sentiment_result = evaluator.evaluate_skill(registry, "sentiment_label", sentiment_cases)

    composed = registry.compose(["normalize_text", "extract_keywords"], composite_name="normalized_keywords")
    composed_output = composed("The Executive strategy chooses strong skills and validation checks their gains.")

    leaderboard = registry.leaderboard()
    csv_path = output_dir / "skill_registry_metrics.csv"
    leaderboard.to_csv(csv_path, index=False)

    plt.figure(figsize=(8, 4))
    plt.bar(leaderboard["name"], leaderboard["avg_score"], color="#4C78A8")
    plt.ylim(0.0, 1.05)
    plt.ylabel("Average score")
    plt.title("Skill registry leaderboard")
    plt.xticks(rotation=20)
    plt.tight_layout()
    figure_path = output_dir / "skill_registry_leaderboard.png"
    plt.savefig(figure_path, dpi=160, bbox_inches="tight")
    plt.close()

    print("Evaluation summary:")
    print(f"- keywords: {keyword_result}")
    print(f"- summary: {summary_result}")
    print(f"- sentiment: {sentiment_result}")
    print(f"- composed normalized keywords: {composed_output}")
    print(f"- saved leaderboard csv: {csv_path}")
    print(f"- saved leaderboard plot: {figure_path}")


if __name__ == "__main__":
    main()
