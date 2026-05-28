"""Metadata extraction utilities for research paper PDFs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import fitz

from extraction.models import PaperMetadata


def extract_metadata(pdf_path: str | Path) -> PaperMetadata:
    """Extract structured metadata from the PDF metadata and first page layout."""

    path = Path(pdf_path)
    document = fitz.open(path)
    pdf_metadata = {key: value for key, value in (document.metadata or {}).items() if value}
    first_page = document[0] if document.page_count else None

    title = _clean_string(pdf_metadata.get("title", ""))
    authors = _split_authors(pdf_metadata.get("author", ""))
    date = _parse_pdf_date(pdf_metadata.get("creationDate") or pdf_metadata.get("modDate"))
    keywords = _split_keywords(pdf_metadata.get("keywords", ""))
    abstract = ""

    if first_page is not None:
        blocks = _page_blocks(first_page)
        page_title, title_index = _extract_title_from_blocks(blocks)
        if not title:
            title = page_title
        page_authors = _extract_authors_from_blocks(blocks, title_index)
        if page_authors:
            authors = page_authors
        abstract = _extract_abstract_from_blocks(blocks)
        page_keywords = _extract_keywords_from_blocks(blocks)
        if page_keywords:
            keywords = page_keywords

    return PaperMetadata(
        title=title,
        authors=authors,
        date=date,
        keywords=keywords,
        abstract=abstract,
        pdf_metadata=pdf_metadata,
    )


def _page_blocks(page: fitz.Page) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for block in page.get_text("dict").get("blocks", []):
        if block.get("type") != 0:
            continue
        lines = block.get("lines", [])
        text = "\n".join(
            "".join(span.get("text", "") for span in line.get("spans", [])).strip()
            for line in lines
            if "".join(span.get("text", "") for span in line.get("spans", [])).strip()
        ).strip()
        if not text:
            continue
        sizes = [float(span.get("size", 0.0)) for line in lines for span in line.get("spans", [])]
        blocks.append(
            {
                "text": text,
                "bbox": tuple(float(value) for value in block.get("bbox", (0.0, 0.0, 0.0, 0.0))),
                "font_size": max(sizes) if sizes else 0.0,
            }
        )
    return sorted(blocks, key=lambda item: (item["bbox"][1], item["bbox"][0]))


def _extract_title_from_blocks(blocks: list[dict[str, Any]]) -> tuple[str, int]:
    if not blocks:
        return "", -1

    candidates = [
        (index, block)
        for index, block in enumerate(blocks)
        if len(block["text"].split()) <= 30 and not re.search(r"@|http", block["text"])
    ]
    if not candidates:
        return "", -1

    title_index, title_block = max(candidates, key=lambda item: (item[1]["font_size"], -item[1]["bbox"][1]))
    return _clean_string(title_block["text"].replace("\n", " ")), title_index


def _extract_authors_from_blocks(blocks: list[dict[str, Any]], title_index: int) -> list[str]:
    if title_index < 0 or title_index >= len(blocks):
        return []

    title_block = blocks[title_index]
    title_bottom = title_block["bbox"][3]
    title_size = float(title_block["font_size"])
    author_lines: list[str] = []

    for block in blocks[title_index + 1 :]:
        text = block["text"].replace("\n", " ").strip()
        if not text:
            continue
        if text.lower().startswith("abstract"):
            break
        if block["bbox"][1] - title_bottom > 140:
            break
        if block["font_size"] >= title_size:
            continue
        if re.search(r"\b(?:university|institute|department|school|laboratory|lab)\b", text, re.IGNORECASE):
            continue
        if re.search(r"@", text):
            continue
        author_lines.append(text)

    return _split_authors(", ".join(author_lines))


def _extract_abstract_from_blocks(blocks: list[dict[str, Any]]) -> str:
    for index, block in enumerate(blocks):
        text = block["text"].strip()
        lowered = text.lower()
        if lowered.startswith("abstract") and len(text) > len("abstract"):
            return text[len("abstract") :].lstrip(" :-\n\t")
        if lowered == "abstract":
            abstract_parts: list[str] = []
            for candidate in blocks[index + 1 :]:
                candidate_text = candidate["text"].strip()
                if candidate_text.lower().startswith("keywords"):
                    break
                if candidate["font_size"] >= block["font_size"] and len(candidate_text.split()) <= 12:
                    break
                abstract_parts.append(candidate_text)
            return "\n".join(abstract_parts).strip()
    return ""


def _extract_keywords_from_blocks(blocks: list[dict[str, Any]]) -> list[str]:
    for block in blocks:
        match = re.search(r"keywords?\s*[:\-]\s*(.+)", block["text"], re.IGNORECASE | re.DOTALL)
        if match:
            return _split_keywords(match.group(1))
    return []


def _split_authors(author_text: str) -> list[str]:
    if not author_text:
        return []
    cleaned = re.sub(r"\s+", " ", author_text.replace("\n", " ")).strip()
    cleaned = re.sub(r"\b(and|&)\b", ",", cleaned, flags=re.IGNORECASE)
    parts = [part.strip(" ,;") for part in re.split(r",|;", cleaned) if part.strip(" ,;")]
    return [part for part in parts if len(part.split()) <= 8]


def _split_keywords(keyword_text: str) -> list[str]:
    if not keyword_text:
        return []
    cleaned = re.sub(r"\s+", " ", keyword_text.replace("\n", " ")).strip()
    return [part.strip(" .;") for part in re.split(r",|;", cleaned) if part.strip(" .;")]


def _parse_pdf_date(raw_date: str | None) -> str | None:
    if not raw_date:
        return None
    match = re.search(r"D:(\d{4})(\d{2})?(\d{2})?", raw_date)
    if not match:
        return raw_date
    year, month, day = match.groups()
    if month and day:
        return f"{year}-{month}-{day}"
    return year


def _clean_string(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()
