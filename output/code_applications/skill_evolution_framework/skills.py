"""Skill definitions for a lightweight self-evolving agent framework."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re
from typing import Any, Callable

SkillFunction = Callable[[str, dict[str, Any]], dict[str, Any]]

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
}

POSITIVE_WORDS = {"excellent", "fast", "great", "helpful", "love", "reliable", "smooth", "stable"}
NEGATIVE_WORDS = {"bad", "broken", "buggy", "confusing", "delay", "hate", "slow", "terrible"}


@dataclass
class Skill:
    """A reusable text-processing skill."""

    name: str
    description: str
    tags: set[str]
    fn: SkillFunction

    def apply(self, text: str, context: dict[str, Any]) -> dict[str, Any]:
        """Apply the skill and merge its outputs into the running context."""
        updates = self.fn(text, context)
        context.update(updates)
        return context


class SkillLibrary:
    """Registry for executable skills."""

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        """Add a skill to the library."""
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        """Return a skill by name."""
        return self._skills[name]

    def names(self) -> list[str]:
        """Return the available skill names."""
        return sorted(self._skills)


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alphabetic words."""
    return re.findall(r"[a-zA-Z']+", text.lower())


def normalize_text_skill(text: str, context: dict[str, Any]) -> dict[str, Any]:
    """Normalize casing and whitespace."""
    normalized = " ".join(text.lower().split())
    updates: dict[str, Any] = {"normalized_text": normalized}
    if context.get("task_type") == "normalize":
        updates["result"] = normalized
    return updates


def split_sentences_skill(text: str, context: dict[str, Any]) -> dict[str, Any]:
    """Split text into simple sentence spans."""
    source = context.get("normalized_text", text)
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", source) if part.strip()]
    return {"sentences": sentences}


def remove_stopwords_skill(text: str, context: dict[str, Any]) -> dict[str, Any]:
    """Filter common stopwords from the current token stream."""
    source = context.get("normalized_text", text)
    filtered_tokens = [token for token in _tokenize(source) if token not in STOPWORDS and len(token) > 2]
    return {"filtered_tokens": filtered_tokens}


def extract_keywords_skill(text: str, context: dict[str, Any]) -> dict[str, Any]:
    """Extract simple frequency-based keywords."""
    tokens = context.get("filtered_tokens") or [token for token in _tokenize(context.get("normalized_text", text)) if token not in STOPWORDS and len(token) > 2]
    counts = Counter(tokens)
    keywords = [word for word, _ in counts.most_common(5)]
    updates: dict[str, Any] = {"keywords": keywords}
    if context.get("task_type") == "keywords":
        updates["result"] = keywords
    return updates


def summarize_text_skill(text: str, context: dict[str, Any]) -> dict[str, Any]:
    """Pick the most salient sentence using keyword overlap when available."""
    sentences = context.get("sentences") or [text.strip()]
    keywords = set(context.get("keywords", []))
    if not keywords:
        summary = sentences[0]
    else:
        scored = []
        for sentence in sentences:
            sentence_tokens = _tokenize(sentence)
            score = sum(token in keywords for token in sentence_tokens)
            scored.append((score, len(sentence_tokens), sentence))
        summary = max(scored, key=lambda item: (item[0], item[1]))[2]
    return {"result": summary.strip()}


def classify_sentiment_skill(text: str, context: dict[str, Any]) -> dict[str, Any]:
    """Classify sentiment with a tiny lexicon-based heuristic."""
    tokens = _tokenize(context.get("normalized_text", text))
    positive_score = sum(token in POSITIVE_WORDS for token in tokens)
    negative_score = sum(token in NEGATIVE_WORDS for token in tokens)
    if positive_score > negative_score:
        label = "positive"
    elif negative_score > positive_score:
        label = "negative"
    else:
        label = "neutral"
    return {"result": label, "sentiment_score": positive_score - negative_score}


def create_default_skill_library() -> SkillLibrary:
    """Build the default set of skills used by the framework demo."""
    library = SkillLibrary()
    library.register(Skill("normalize_text", "Normalize casing and whitespace.", {"cleanup", "text"}, normalize_text_skill))
    library.register(Skill("split_sentences", "Split text into sentences.", {"structure", "summary"}, split_sentences_skill))
    library.register(Skill("remove_stopwords", "Drop uninformative words.", {"cleanup", "keywords"}, remove_stopwords_skill))
    library.register(Skill("extract_keywords", "Extract frequent keywords.", {"analysis", "keywords", "summary"}, extract_keywords_skill))
    library.register(Skill("summarize_text", "Produce a concise summary sentence.", {"summary", "generation"}, summarize_text_skill))
    library.register(Skill("classify_sentiment", "Predict coarse sentiment.", {"analysis", "sentiment"}, classify_sentiment_skill))
    return library


if __name__ == "__main__":
    demo_library = create_default_skill_library()
    print("Available skills:")
    for name in demo_library.names():
        print(f"- {name}")
