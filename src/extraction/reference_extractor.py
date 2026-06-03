"""Reference and citation extraction utilities for research paper PDFs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

import fitz

from extraction.models import Reference, Section
from extraction.text_extractor import extract_text_sections

_URL_PATTERN = re.compile(r"(?:https?://\S+|www\.\S+)", re.IGNORECASE)
_DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
_ARXIV_PATTERN = re.compile(r"arXiv:\s*(\d{4}\.\d{4,5}(?:v\d+)?)", re.IGNORECASE)


def extract_references(
    pdf_path: str | Path,
    sections: Sequence[Section] | None = None,
    full_text: str | None = None,
) -> dict[str, list[Reference] | list[str]]:
    """Extract bibliography entries, in-text citations, and URLs from a PDF."""

    pdf = Path(pdf_path)
    if sections is None or full_text is None:
        text_data = extract_text_sections(pdf)
        sections = text_data["sections"]
        full_text = text_data["full_text"]

    references_text = _locate_reference_text(sections or [], full_text or "")
    reference_entries = _split_reference_entries(references_text)
    references = [_parse_reference(entry) for entry in reference_entries if entry.strip()]
    citations = sorted(set(re.findall(r"\[\d+(?:\s*[-,]\s*\d+)*\]", full_text or "")))
    citations.extend(sorted(set(re.findall(r"\([A-Z][A-Za-z'`-]+(?:\s+et\s+al\.)?,\s*(?:19|20)\d{2}[a-z]?\)", full_text or ""))))
    urls = sorted(set(_URL_PATTERN.findall(full_text or "")))
    urls.extend(_extract_pdf_links(pdf))

    deduped_urls = sorted(set(url.strip(").,;") for url in urls if url))
    deduped_citations = sorted(set(citations))
    return {
        "references": references,
        "in_text_citations": deduped_citations,
        "urls": deduped_urls,
    }


def _locate_reference_text(sections: Sequence[Section], full_text: str) -> str:
    for section in sections:
        normalized = section.title.strip().lower()
        if normalized in {"references", "bibliography", "works cited"}:
            return section.content

    match = re.search(
        r"(?:^|\n)(references|bibliography|works cited)\s*\n(?P<body>.+)$",
        full_text,
        re.IGNORECASE | re.DOTALL,
    )
    return match.group("body").strip() if match else ""


def _split_reference_entries(references_text: str) -> list[str]:
    if not references_text:
        return []

    lines = [line.strip() for line in references_text.splitlines() if line.strip()]
    entries: list[str] = []
    current: list[str] = []

    for line in lines:
        if _is_reference_start(line) and current:
            entries.append(" ".join(current).strip())
            current = [line]
        else:
            current.append(line)

    if current:
        entries.append(" ".join(current).strip())

    return entries


def _is_reference_start(line: str) -> bool:
    """Detect if a line starts a new reference entry."""
    return bool(
        # Numbered: [1], [2] or 1., 2.
        re.match(r"^(\[\d+\]|\d+\.)\s+", line)
        # Author last name, first initial: Smith, J.
        or re.match(r"^[A-Z][A-Za-z'`-]+,\s+[A-Z][\.,]", line)
        # Author-year: Smith et al., 2020 or Smith, 2020
        or re.match(r"^[A-Z][A-Za-z'`-]+(?:\s+et\s+al\.)?,\s*(?:19|20)\d{2}", line)
        # arXiv format: arXiv:1234.5678
        or re.match(r"^arXiv:", line, re.IGNORECASE)
    )


def _parse_reference(entry: str) -> Reference:
    """Parse a single reference entry into structured fields."""
    raw = re.sub(r"\s+", " ", entry).strip()
    
    # Extract patterns
    year_match = re.search(r"\b(?:19|20)\d{2}[a-z]?\b", raw)
    doi_match = _DOI_PATTERN.search(raw)
    url_match = _URL_PATTERN.search(raw)
    arxiv_match = _ARXIV_PATTERN.search(raw)
    
    # Parse authors (text before year or before first period)
    if year_match:
        authors_part = raw[: year_match.start()].strip(" .,[]0-9")
    else:
        authors_part = raw.split(".", maxsplit=1)[0].strip(" .,[]0-9")
    
    # Clean up authors list
    authors_part = re.sub(r"^\[\d+\]\s*", "", authors_part)  # Remove leading [1]
    authors = []
    for part in re.split(r"\band\b|,|;", authors_part):
        cleaned = part.strip()
        if cleaned and len(cleaned.split()) <= 8 and not re.match(r"^\d+$", cleaned):
            authors.append(cleaned)
    
    # Extract title (quoted text or text after year)
    title = None
    # Try quoted title first (both regular and Unicode quotes)
    title_match = re.search(r'[""\'"]([^""\'\']+)[""\'"]', raw)
    if title_match and len(title_match.groups()) > 0:
        title = title_match.group(1).strip()
    # Try title after year
    elif year_match:
        after_year = raw[year_match.end() :].strip(" .,:")
        if after_year:
            # Title is usually before venue/journal
            parts = re.split(r"\.\s+(?:In\s+|Proceedings\s+|Journal\s+|Conference\s+)", after_year, maxsplit=1)
            title = parts[0].strip() if parts[0] else None
    
    # Extract venue (conference/journal after title)
    venue = None
    if title and title in raw:
        after_title = raw.split(title, maxsplit=1)[-1].strip(" .,")
        if after_title:
            # Look for venue patterns
            venue_match = re.search(
                r"(?:In\s+|Proceedings\s+of\s+|Journal\s+of\s+|Conference\s+on\s+)?([^.,]+(?:Conference|Workshop|Symposium|Journal|Transactions|Proceedings)[^.,]*)",
                after_title,
                re.IGNORECASE
            )
            if venue_match:
                venue = venue_match.group(0).strip()
            else:
                # Fallback: first sentence after title
                venue = after_title.split(".", maxsplit=1)[0].strip()[:100]
    
    return Reference(
        raw_text=raw,
        authors=authors[:10],  # Limit to first 10 authors
        title=title,
        year=year_match.group(0) if year_match else None,
        venue=venue,
        doi=doi_match.group(0) if doi_match else None,
        url=(arxiv_match.group(0) if arxiv_match else None) or (url_match.group(0).strip(").,;") if url_match else None),
    )


def _extract_pdf_links(pdf_path: Path) -> list[str]:
    urls: list[str] = []
    document = fitz.open(pdf_path)
    for page in document:
        for link in page.get_links():
            uri = link.get("uri")
            if uri:
                urls.append(str(uri))
    return urls
