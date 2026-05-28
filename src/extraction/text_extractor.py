"""Text extraction utilities for research paper PDFs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any

import fitz
import numpy as np

from extraction.models import Section


@dataclass(slots=True)
class _TextBlock:
    page_number: int
    text: str
    bbox: tuple[float, float, float, float]
    font_size: float
    bold_ratio: float


def extract_text_sections(pdf_path: str | Path) -> dict[str, Any]:
    """Extract full text, abstract, and structured sections from a PDF."""

    path = Path(pdf_path)
    document = fitz.open(path)

    blocks: list[_TextBlock] = []
    for page_index in range(document.page_count):
        page = document[page_index]
        blocks.extend(_extract_page_blocks(page, page_index + 1))

    if not blocks:
        return {"abstract": "", "full_text": "", "sections": []}

    font_sizes = [block.font_size for block in blocks if block.font_size > 0]
    median_size = median(font_sizes) if font_sizes else 10.0
    upper_size = float(np.percentile(font_sizes, 75)) if font_sizes else median_size

    abstract = _extract_abstract(blocks, median_size, upper_size)
    sections = _build_sections(blocks, abstract, median_size, upper_size)
    full_text = "\n\n".join(block.text for block in blocks if block.text)

    return {
        "abstract": abstract,
        "full_text": full_text,
        "sections": sections,
    }


def _extract_page_blocks(page: fitz.Page, page_number: int) -> list[_TextBlock]:
    page_dict = page.get_text("dict")
    raw_blocks = [block for block in page_dict.get("blocks", []) if block.get("type") == 0]
    sorted_blocks = _sort_blocks_for_reading_order(raw_blocks, page.rect.width, page.rect.height)

    blocks: list[_TextBlock] = []
    for block in sorted_blocks:
        text_parts: list[str] = []
        sizes: list[float] = []
        bold_chars = 0
        total_chars = 0

        for line in block.get("lines", []):
            line_text = "".join(span.get("text", "") for span in line.get("spans", []))
            if line_text.strip():
                text_parts.append(line_text.strip())
            for span in line.get("spans", []):
                span_text = span.get("text", "")
                span_size = float(span.get("size", 0.0))
                sizes.append(span_size)
                total_chars += len(span_text)
                if _is_bold_font(span.get("font", ""), int(span.get("flags", 0))):
                    bold_chars += len(span_text)

        text = "\n".join(part for part in text_parts if part).strip()
        if not text:
            continue

        bbox = tuple(float(value) for value in block.get("bbox", (0.0, 0.0, 0.0, 0.0)))
        font_size = max(sizes) if sizes else 0.0
        bold_ratio = bold_chars / total_chars if total_chars else 0.0
        blocks.append(
            _TextBlock(
                page_number=page_number,
                text=text,
                bbox=bbox,
                font_size=font_size,
                bold_ratio=bold_ratio,
            )
        )

    return blocks


def _sort_blocks_for_reading_order(
    blocks: list[dict[str, Any]],
    page_width: float,
    page_height: float,
) -> list[dict[str, Any]]:
    if len(blocks) < 4:
        return sorted(blocks, key=lambda block: (block.get("bbox", [0, 0, 0, 0])[1], block.get("bbox", [0, 0, 0, 0])[0]))

    narrow_blocks = []
    for block in blocks:
        x0, y0, x1, _ = block.get("bbox", (0.0, 0.0, 0.0, 0.0))
        width_ratio = (x1 - x0) / max(page_width, 1.0)
        if width_ratio < 0.55:
            narrow_blocks.append(block)

    left_count = sum(1 for block in narrow_blocks if ((block.get("bbox", [0, 0, 0, 0])[0] + block.get("bbox", [0, 0, 0, 0])[2]) / 2) < page_width / 2)
    right_count = len(narrow_blocks) - left_count
    is_multicolumn = left_count >= 2 and right_count >= 2

    if not is_multicolumn:
        return sorted(blocks, key=lambda block: (block.get("bbox", [0, 0, 0, 0])[1], block.get("bbox", [0, 0, 0, 0])[0]))

    top_full: list[dict[str, Any]] = []
    left: list[dict[str, Any]] = []
    right: list[dict[str, Any]] = []
    bottom_full: list[dict[str, Any]] = []

    for block in blocks:
        x0, y0, x1, _ = block.get("bbox", (0.0, 0.0, 0.0, 0.0))
        width_ratio = (x1 - x0) / max(page_width, 1.0)
        center = (x0 + x1) / 2
        if width_ratio >= 0.6 and y0 < page_height * 0.35:
            top_full.append(block)
        elif width_ratio >= 0.6:
            bottom_full.append(block)
        elif center < page_width / 2:
            left.append(block)
        else:
            right.append(block)

    sort_key = lambda block: (block.get("bbox", [0, 0, 0, 0])[1], block.get("bbox", [0, 0, 0, 0])[0])
    return sorted(top_full, key=sort_key) + sorted(left, key=sort_key) + sorted(right, key=sort_key) + sorted(bottom_full, key=sort_key)


def _extract_abstract(blocks: list[_TextBlock], median_size: float, upper_size: float) -> str:
    first_page_blocks = [block for block in blocks if block.page_number == 1]
    if not first_page_blocks:
        return ""

    for index, block in enumerate(first_page_blocks):
        inline = _strip_abstract_label(block.text)
        if inline and inline != block.text:
            return inline

        normalized = block.text.strip().lower()
        if normalized in {"abstract", "summary"} or normalized.startswith("abstract\n"):
            abstract_parts: list[str] = []
            for candidate in first_page_blocks[index + 1 :]:
                if _is_heading(candidate, median_size, upper_size) and not candidate.text.lower().startswith("abstract"):
                    break
                abstract_parts.append(_strip_abstract_label(candidate.text))
            return "\n".join(part for part in abstract_parts if part).strip()

    return ""


def _build_sections(
    blocks: list[_TextBlock],
    abstract: str,
    median_size: float,
    upper_size: float,
) -> list[Section]:
    sections: list[Section] = []
    current_title = "Introduction"
    current_content: list[str] = []
    current_start_page = 1
    abstract_consumed = False

    for block in blocks:
        if block.page_number == 1 and abstract and not abstract_consumed and _normalize_text(block.text) in _normalize_text(abstract):
            abstract_consumed = True
            continue

        if block.page_number == 1 and block.font_size >= upper_size + 1.5:
            continue

        if _is_heading(block, median_size, upper_size) and block.text.strip().lower() not in {"abstract", "summary"}:
            if current_content:
                sections.append(
                    Section(
                        title=current_title,
                        content="\n\n".join(current_content).strip(),
                        page_start=current_start_page,
                        page_end=block.page_number,
                        level=_heading_level(block.font_size, upper_size),
                    )
                )
            current_title = block.text.replace("\n", " ").strip()
            current_content = []
            current_start_page = block.page_number
            continue

        current_content.append(block.text)

    if current_content:
        sections.append(
            Section(
                title=current_title,
                content="\n\n".join(current_content).strip(),
                page_start=current_start_page,
                page_end=blocks[-1].page_number,
                level=1,
            )
        )

    return [section for section in sections if section.content]


def _is_heading(block: _TextBlock, median_size: float, upper_size: float) -> bool:
    text = block.text.replace("\n", " ").strip()
    if not text or len(text) > 180:
        return False

    words = text.split()
    if len(words) > 16:
        return False

    if text.endswith((".", ";", ":")) and not text.lower().startswith(("abstract", "keywords")):
        return False

    numbered = bool(np.re_match(r"^(?:\d+(?:\.\d+)*|[IVX]+)\s+", text)) if hasattr(np, "re_match") else False
    numbered = numbered or bool(__import__("re").match(r"^(?:\d+(?:\.\d+)*|[IVX]+)\s+", text))
    title_case = text == text.title()
    all_caps = text.isupper() and len(words) <= 10
    prominent = block.font_size >= upper_size or block.font_size >= median_size + 1.2
    bold = block.bold_ratio >= 0.45

    return numbered or all_caps or ((prominent or bold) and (title_case or len(words) <= 8))


def _heading_level(font_size: float, upper_size: float) -> int:
    return 1 if font_size >= upper_size + 0.5 else 2


def _strip_abstract_label(text: str) -> str:
    cleaned = text.strip()
    lowered = cleaned.lower()
    for prefix in ("abstract", "summary"):
        if lowered.startswith(prefix):
            remainder = cleaned[len(prefix) :].lstrip(" :-\n\t")
            return remainder.strip()
    return cleaned


def _normalize_text(text: str) -> str:
    return " ".join(text.split())


def _is_bold_font(font_name: str, flags: int) -> bool:
    lowered = font_name.lower()
    return "bold" in lowered or "medi" in lowered or bool(flags & 16)
