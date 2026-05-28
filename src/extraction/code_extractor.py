"""Code block extraction utilities for research paper PDFs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import fitz

from extraction.models import CodeBlock


_MONOSPACE_FONTS = ("courier", "consolas", "menlo", "monaco", "code", "mono")


@dataclass(slots=True)
class _LineCandidate:
    text: str
    page_number: int
    bbox: tuple[float, float, float, float]
    monospace_ratio: float
    is_code: bool


def extract_code_blocks(pdf_path: str | Path) -> list[CodeBlock]:
    """Detect code snippets in a PDF using font and formatting heuristics."""

    pdf = Path(pdf_path)
    document = fitz.open(pdf)
    candidates: list[_LineCandidate] = []

    for page_index in range(document.page_count):
        page = document[page_index]
        for line in _extract_lines(page, page_index + 1):
            candidates.append(line)

    return _group_code_lines(candidates)


def _extract_lines(page: fitz.Page, page_number: int) -> list[_LineCandidate]:
    lines: list[_LineCandidate] = []
    for block in page.get_text("dict").get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            text = "".join(span.get("text", "") for span in spans).rstrip()
            if not text.strip():
                continue
            monospace_chars = sum(len(span.get("text", "")) for span in spans if _is_monospace_font(span.get("font", "")))
            total_chars = sum(len(span.get("text", "")) for span in spans) or 1
            monospace_ratio = monospace_chars / total_chars
            bbox = tuple(float(value) for value in line.get("bbox", (0.0, 0.0, 0.0, 0.0)))
            is_code = _looks_like_code(text, monospace_ratio)
            lines.append(_LineCandidate(text=text, page_number=page_number, bbox=bbox, monospace_ratio=monospace_ratio, is_code=is_code))
    return sorted(lines, key=lambda item: (item.page_number, item.bbox[1], item.bbox[0]))


def _group_code_lines(lines: list[_LineCandidate]) -> list[CodeBlock]:
    code_blocks: list[CodeBlock] = []
    current: list[_LineCandidate] = []
    previous_text = ""

    for index, line in enumerate(lines):
        if line.is_code:
            current.append(line)
            previous_text = lines[index - 1].text if index > 0 else ""
            continue

        if current:
            block = _finalize_block(current, previous_text, line.text)
            if block is not None:
                code_blocks.append(block)
            current = []
            previous_text = ""

    if current:
        block = _finalize_block(current, previous_text, "")
        if block is not None:
            code_blocks.append(block)

    return code_blocks


def _finalize_block(current: list[_LineCandidate], previous_text: str, next_text: str) -> CodeBlock | None:
    content = "\n".join(line.text for line in current).strip()
    if len(current) < 2 and len(content) < 50:
        return None
    first = current[0]
    last = current[-1]
    bbox = (
        min(line.bbox[0] for line in current),
        min(line.bbox[1] for line in current),
        max(line.bbox[2] for line in current),
        max(line.bbox[3] for line in current),
    )
    context = " ".join(part.strip() for part in (previous_text, next_text) if part.strip())
    return CodeBlock(
        language=_detect_language(content),
        content=content,
        page_number=first.page_number,
        context=context,
        bbox=bbox,
    )


def _looks_like_code(text: str, monospace_ratio: float) -> bool:
    stripped = text.rstrip()
    if monospace_ratio >= 0.6:
        return True
    if stripped.startswith(("    ", "\t")):
        return True
    if re.search(r"[{};<>:=()]", stripped) and re.search(r"\b(def|class|for|if|while|return|import|function|public|private|const|let)\b", stripped):
        return True
    if re.match(r"^(from|import|def|class|for|if|while|return|SELECT|INSERT|UPDATE|CREATE|function|const|let)\b", stripped):
        return True
    return False


def _detect_language(content: str) -> str | None:
    scores = {
        "python": len(re.findall(r"\b(def|import|from|class|elif|None|True|False)\b", content)),
        "javascript": len(re.findall(r"\b(function|const|let|var|=>|console\.log)\b", content)),
        "java": len(re.findall(r"\b(public|private|class|static|void|System\.out)\b", content)),
        "sql": len(re.findall(r"\b(SELECT|FROM|WHERE|JOIN|GROUP BY|ORDER BY|INSERT|UPDATE|DELETE)\b", content, re.IGNORECASE)),
        "bash": len(re.findall(r"\b(echo|grep|cd|ls|cat|export|python)\b", content)),
        "json": 1 if content.strip().startswith(("{", "[")) and '"' in content else 0,
    }
    language, score = max(scores.items(), key=lambda item: item[1])
    return language if score > 0 else None


def _is_monospace_font(font_name: str) -> bool:
    lowered = font_name.lower()
    return any(token in lowered for token in _MONOSPACE_FONTS)
